import operator

from django.conf import settings
from django.db import transaction
from django.db.models import F

from comments.choices import Vote
from comments.exceptions import CommentVoteException
from comments.models import Comment, CommentVote
from users.models import UserPublic


def update_post_comments_count(comment: Comment, added: bool = True):
    """Update comments count fot the post comment posted on."""
    post = comment.post
    operation = {
        True: operator.add,
        False: operator.sub,
    }[added]
    post.comments_count = operation(F("comments_count"), 1)
    post.save(update_fields=["comments_count"])


def update_author_comments_count(comment: Comment, added: bool = True):
    author = comment.user
    operation = {
        True: operator.add,
        False: operator.sub,
    }[added]
    author.comments_count = operation(F("comments_count"), 1)
    author.save(update_fields=["comments_count"])


@transaction.atomic
def record_vote_for_comment(comment: Comment, actor: UserPublic, vote: Vote):
    """Record vote for a comment and trigger updates of comment and comment's author.

    Raises
    ------
    CommentVoteException
        In case when user tries to vote for its own post, or vote twice
    """

    if comment.user_id == actor.id:
        raise CommentVoteException("Не надо голосовать за свой же пост.")

    comment_vote = CommentVote.objects.filter(comment=comment, user=actor).first()
    vote_cancelled = False
    if comment_vote:
        if comment_vote.value == vote:
            raise CommentVoteException("Не надо голосовать второй раз за пост.")
        # Здесь если при наличии голоса, пользователь проголосовал еще раз, но
        # противоположно - отменяем рейтинг и удаляем PostVote
        vote_cancelled = True
        comment_vote.delete()
    else:
        comment_vote = CommentVote.objects.create(comment=comment, user=actor, value=vote)

    update_comment_rating_on_vote(comment_vote, vote_cancelled)
    update_author_rating_on_comment_vote(comment_vote, vote_cancelled)
    update_voter_votes_count_on_comment_vote(comment_vote, vote_cancelled)


def update_author_rating_on_comment_vote(
    comment_vote: CommentVote, vote_cancelled: bool = False
):
    """Update author rating when its comment gets vote."""
    operation = {
        True: operator.sub,
        False: operator.add,
    }[vote_cancelled]

    author = comment_vote.comment.user
    author.rating = operation(
        F("rating"), get_comment_vote_value_for_author(author, comment_vote.value)
    )
    author.save(update_fields=["rating"])


def update_voter_votes_count_on_comment_vote(
    comment_vote: CommentVote, vote_cancelled: bool = False
):
    """Update votes counts for voter."""
    voter: UserPublic = comment_vote.user
    operation = {
        True: operator.sub,
        False: operator.add,
    }[vote_cancelled]
    if comment_vote.value == Vote.UPVOTE:
        voter.votes_up_count = operation(F("votes_up_count"), 1)
    else:
        voter.votes_down_count = operation(F("votes_down_count"), 1)
    voter.save()


def update_comment_rating_on_vote(
    comment_vote: CommentVote, vote_cancelled: bool = False
):
    """Update comment rating when it gets vote."""
    operation = {
        True: operator.sub,
        False: operator.add,
    }[vote_cancelled]

    comment: Comment = comment_vote.comment
    comment.rating = operation(F("rating"), comment_vote.value)
    if comment_vote.value == Vote.UPVOTE:
        comment.votes_up_count = operation(F("votes_up_count"), 1)
    else:
        comment.votes_down_count = operation(F("votes_down_count"), 1)
    comment.save()


def get_comment_vote_value_for_author(author: UserPublic, value: Vote) -> float:
    return value * settings.COMMENT_RATING_MULTIPLIER
