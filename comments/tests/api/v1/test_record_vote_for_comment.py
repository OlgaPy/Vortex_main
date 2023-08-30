import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from comments.choices import Vote
from comments.services import get_comment_vote_value_for_author
from comments.tests.factories import CommentFactory
from users.tests.factories import UserPublicFactory


@pytest.mark.django_db
class TestRecordVoteForComment:
    def setup(self):
        self.comment_original_rating = 10
        self.comment_original_votes_up_count = 20
        self.comment_original_votes_down_count = 10
        self.author_original_rating = 15
        self.comment = CommentFactory(
            user=UserPublicFactory(rating=self.author_original_rating),
            rating=self.comment_original_rating,
            votes_up_count=self.comment_original_votes_up_count,
            votes_down_count=self.comment_original_votes_down_count,
        )
        self.voter_original_votes_up_count = 5
        self.voter_original_votes_down_count = 7
        self.voter = UserPublicFactory(
            votes_up_count=self.voter_original_votes_up_count,
            votes_down_count=self.voter_original_votes_down_count,
        )

    @pytest.mark.parametrize(
        "vote_value,expected_votes_count,expected_comment_rating",
        [
            (Vote.UPVOTE, 1, 1),
            (Vote.DOWNVOTE, 1, -1),
        ],
    )
    def test_voting_first_time(
        self,
        authed_api_client,
        vote_value,
        expected_votes_count,
        expected_comment_rating,
    ):
        client = authed_api_client(self.voter)
        result = self._vote_for_comment(client, self.comment, vote_value)

        rating_value = get_comment_vote_value_for_author(self.comment.user, vote_value)

        assert result.status_code == status.HTTP_201_CREATED, result.content.decode()

        self.comment.refresh_from_db()
        self.voter.refresh_from_db()

        expected_comment_rating = self.comment_original_rating + expected_comment_rating
        expected_comment_user_rating = self.author_original_rating + rating_value

        assert self.comment.user.rating == expected_comment_user_rating

        if vote_value == Vote.UPVOTE:
            assert self.voter.votes_up_count == self.voter_original_votes_up_count + 1
        else:
            assert self.voter.votes_down_count == self.voter_original_votes_down_count + 1

        assert result.data == {
            "uuid": str(self.comment.uuid),
            "votes_up_count": self.comment_original_votes_up_count + 1
            if vote_value == Vote.UPVOTE
            else self.comment_original_votes_up_count,
            "votes_down_count": self.comment_original_votes_down_count + 1
            if vote_value == Vote.DOWNVOTE
            else self.comment_original_votes_down_count,
            "rating": expected_comment_rating,
        }

    @pytest.mark.parametrize("vote_value", (Vote.UPVOTE, Vote.DOWNVOTE))
    def test_voting_for_own_comment(self, authed_api_client, vote_value):
        client = authed_api_client(self.comment.user)
        result = self._vote_for_comment(client, self.comment, vote_value)
        assert result.status_code == status.HTTP_201_CREATED

    @pytest.mark.parametrize("second_vote", (Vote.UPVOTE, Vote.DOWNVOTE))
    @pytest.mark.parametrize("first_vote", (Vote.UPVOTE, Vote.DOWNVOTE))
    def test_undo_vote(self, authed_api_client, first_vote, second_vote):
        client = authed_api_client(self.voter)
        self._vote_for_comment(client, self.comment, first_vote)
        result = self._vote_for_comment(client, self.comment, second_vote)
        assert result.status_code == status.HTTP_201_CREATED, result.content.decode()

        assert result.data == {
            "uuid": str(self.comment.uuid),
            "votes_up_count": self.comment_original_votes_up_count,
            "votes_down_count": self.comment_original_votes_down_count,
            "rating": self.comment_original_rating,
        }
        self.comment.user.refresh_from_db()
        assert self.comment.user.rating == self.author_original_rating
        self.voter.refresh_from_db()
        assert self.voter.votes_up_count == self.voter_original_votes_up_count
        assert self.voter.votes_down_count == self.voter_original_votes_down_count

    def test_cant_vote_as_anonymous(self, anon_api_client):
        result = self._vote_for_comment(anon_api_client(), self.comment, Vote.UPVOTE)
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cant_vote_with_wrong_values(self, authed_api_client):
        client = authed_api_client(self.voter)
        result = self._vote_for_comment(client, self.comment, 10)
        assert result.status_code == status.HTTP_400_BAD_REQUEST

    def test_cant_vote_non_active(self, authed_api_client):
        voter = UserPublicFactory(is_active=False)
        client = authed_api_client(voter)
        result = self._vote_for_comment(client, self.comment, Vote.UPVOTE)
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def _vote_for_comment(self, client, comment, vote_value):
        return client.post(
            reverse("v1:comments:comments-vote", kwargs={"uuid": comment.uuid}),
            data={"value": vote_value},
        )
