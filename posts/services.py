import operator

from django.db import transaction
from django.db.models import F

from posts.choices import Vote
from posts.exceptions import PostVoteException
from posts.models import PostVote, Post
from users.models import UserPublic


def update_author_rating_on_post_vote(
    post_vote: PostVote, vote_cancelled: bool = False
):
    operation = {
        True: operator.sub,
        False: operator.add,
    }[vote_cancelled]
    author = post_vote.post.user

    author.rating = operation(F("rating"), post_vote.value)

    author.save(update_fields=["rating"])


def update_post_rating_on_vote(post_vote: PostVote, vote_cancelled: bool = False):
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
def record_vote_for_post(post: Post, user: UserPublic, vote: Vote):
    if post.user_id == user.id:
        raise PostVoteException("Не надо голосовать за свой же пост.")

    post_vote = PostVote.objects.filter(post=post, user=user).first()
    vote_cancelled = False
    if post_vote:
        if post_vote.value == vote:
            raise PostVoteException("Не надо голосовать второй раз за пост.")
        # Здесь если при наличии голоса, пользователь проголосовал еще раз, но
        # противоположно - отменяем рейтинг и удаляем PostVote
        vote_cancelled = True
        post_vote.delete()
    else:
        post_vote = PostVote.objects.create(post=post, user=user, value=vote)

    update_post_rating_on_vote(post_vote, vote_cancelled)
    update_author_rating_on_post_vote(post_vote, vote_cancelled)
