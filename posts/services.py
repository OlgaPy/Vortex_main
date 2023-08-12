import logging
import operator

from django.db import transaction
from django.db.models import F

from posts.choices import PostStatus, Vote
from posts.exceptions import PostDeleteException, PostPublishException, PostVoteException
from posts.models import Post, PostVote
from users.models import UserPublic

logger = logging.getLogger(__name__)


def update_author_rating_on_post_vote(post_vote: PostVote, vote_cancelled: bool = False):
    """Update author rating when it's post gets vote."""
    operation = {
        True: operator.sub,
        False: operator.add,
    }[vote_cancelled]

    author = post_vote.post.user
    author.rating = operation(F("rating"), post_vote.value)
    author.save(update_fields=["rating"])


def update_post_rating_on_vote(post_vote: PostVote, vote_cancelled: bool = False):
    """Update post rating when it gets vote."""
    operation = {
        True: operator.sub,
        False: operator.add,
    }[vote_cancelled]

    post = post_vote.post
    post.rating = operation(F("rating"), post_vote.value)
    if post_vote.value == Vote.UPVOTE:
        post.votes_up_count = operation(F("votes_up_count"), 1)
    else:
        post.votes_down_count = operation(F("votes_down_count"), 1)
    post.save()


@transaction.atomic
def record_vote_for_post(post: Post, actor: UserPublic, vote: Vote):
    """Record vote for a post and trigger updates of post and post's author.

    Raises
    ------
    PostVoteException
        In case when user tries to vote for its own post, or vote twice
    """
    if post.user_id == actor.id:
        raise PostVoteException("Не надо голосовать за свой же пост.")

    post_vote = PostVote.objects.filter(post=post, user=actor).first()
    vote_cancelled = False
    if post_vote:
        if post_vote.value == vote:
            raise PostVoteException("Не надо голосовать второй раз за пост.")
        # Здесь если при наличии голоса, пользователь проголосовал еще раз, но
        # противоположно - отменяем рейтинг и удаляем PostVote
        vote_cancelled = True
        post_vote.delete()
    else:
        post_vote = PostVote.objects.create(post=post, user=actor, value=vote)

    update_post_rating_on_vote(post_vote, vote_cancelled)
    update_author_rating_on_post_vote(post_vote, vote_cancelled)


def publish_post(post: Post, actor: UserPublic) -> Post:
    """Publish the post.

    Raises
    ------
    PostPublishException
        In case user trying to publish not own post, or deleted post
    """
    if post.user != actor:
        raise PostPublishException("Нельзя публиковать чужой пост!")

    if post.status == PostStatus.DELETED:
        raise PostPublishException("Нельзя публиковать удаленный пост!")

    if post.status == PostStatus.DRAFT:
        logger.info("Post %s published by %s", post, actor)
        post.status = PostStatus.PUBLISHED
        post.save()

    return post


def delete_post(post: Post, actor: UserPublic):
    """Mark post as deleted.

    Raises
    ------
    PostDeleteException
        When user tries to delete someone else's post
    """
    if post.user != actor:
        raise PostDeleteException("Нельзя удалять чужие посты!")

    if post.status == PostStatus.DELETED:
        return

    logger.info("Post %s deleted by %s", post, actor)
    post.status = PostStatus.DELETED
    post.save()
