import pytest

from users.choices import Vote
from users.models import PostVote, CommentVote
from users.services import (
    update_author_rating_on_post_vote,
    update_author_rating_on_comment_vote,
)
from users.tests.factories import PostVoteFactory, CommentVoteFactory


@pytest.mark.django_db
@pytest.mark.parametrize(
    "vote_value,expected_user_rating",
    (
        (Vote.UPVOTE, 1),
        (Vote.DOWNVOTE, -1),
    ),
)
def test_update_author_rating_on_post_vote(vote_value, expected_user_rating):
    vote = PostVoteFactory(value=vote_value)
    user = vote.post.user
    assert user.rating == 0
    update_author_rating_on_post_vote(vote)

    user.refresh_from_db()
    assert user.rating == expected_user_rating


@pytest.mark.django_db
@pytest.mark.parametrize(
    "vote_value,expected_user_rating",
    (
        (Vote.UPVOTE, 0.5),
        (Vote.DOWNVOTE, -0.5),
    ),
)
def test_update_author_rating_on_comment_vote(vote_value, expected_user_rating):
    vote = CommentVoteFactory(value=vote_value)
    user = vote.comment.user
    assert user.rating == 0
    update_author_rating_on_comment_vote(vote)

    user.refresh_from_db()
    assert user.rating == expected_user_rating
