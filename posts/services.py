import logging
import operator

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from posts.choices import PostStatus, Vote
from posts.exceptions import PostDeleteException, PostPublishException
from posts.models import Post, PostVote
from posts.selectors import get_post_vote_value_for_author
from users.models import UserPublic

logger = logging.getLogger(__name__)


def update_author_rating_on_post_vote(post_vote: PostVote, vote_cancelled: bool = False):
    """Update author rating when it's post gets vote."""
    operation = {
        True: operator.sub,
        False: operator.add,
    }[vote_cancelled]

    author = post_vote.post.user
    author.rating = operation(
        F("rating"), get_post_vote_value_for_author(author, post_vote)
    )
    author.save(update_fields=["rating"])


def update_voter_votes_count_on_post_vote(
    post_vote: PostVote, vote_cancelled: bool = False
):
    """Update votes counts for voter."""
    voter: UserPublic = post_vote.user
    operation = {
        True: operator.sub,
        False: operator.add,
    }[vote_cancelled]
    if post_vote.value == Vote.UPVOTE:
        voter.votes_up_count = operation(F("votes_up_count"), 1)
    else:
        voter.votes_down_count = operation(F("votes_down_count"), 1)
    voter.save()


def update_post_rating_on_vote(post_vote: PostVote, vote_cancelled: bool = False):
    """Update post rating when it gets vote."""
    operation = {
        True: operator.sub,
        False: operator.add,
    }[vote_cancelled]

    post: Post = post_vote.post
    post.rating = operation(F("rating"), post_vote.value)
    if post_vote.value == Vote.UPVOTE:
        post.votes_up_count = operation(F("votes_up_count"), 1)
    else:
        post.votes_down_count = operation(F("votes_down_count"), 1)
    post.save()


@transaction.atomic
def record_vote_for_post(post: Post, actor: UserPublic, vote: Vote):
    """Record vote for a post and trigger updates of post and post's author."""
    post_vote = PostVote.objects.filter(post=post, user=actor).first()
    vote_cancelled = False
    if post_vote:
        # Здесь если при наличии голоса, пользователь проголосовал еще раз,
        # отменяем рейтинг и удаляем PostVote
        vote_cancelled = True
        post_vote.delete()
    else:
        post_vote = PostVote.objects.create(post=post, user=actor, value=vote)

    update_post_rating_on_vote(post_vote, vote_cancelled)
    update_author_rating_on_post_vote(post_vote, vote_cancelled)
    update_voter_votes_count_on_post_vote(post_vote, vote_cancelled)


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
        post.published_at = timezone.now()
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
