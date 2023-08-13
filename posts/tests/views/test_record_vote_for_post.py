import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from posts.choices import PostStatus, Vote
from posts.tests.factories import PostFactory, PostVoteFactory
from users.tests.factories import UserPublicFactory


@pytest.mark.django_db
class TestRecordVoteForPost:
    def setup(self):
        self.post_original_rating = 10
        self.post_original_votes_up_count = 20
        self.post_original_votes_down_count = 10
        self.author_original_rating = 15
        self.post = PostFactory(
            user=UserPublicFactory(rating=self.author_original_rating),
            status=PostStatus.PUBLISHED,
            rating=self.post_original_rating,
            votes_up_count=self.post_original_votes_up_count,
            votes_down_count=self.post_original_votes_down_count,
        )
        self.voter = UserPublicFactory()

    @pytest.mark.parametrize(
        "vote_value,expected_votes_count,expected_post_rating,expected_post_user_rating",
        [
            (Vote.UPVOTE, 1, 1, 1),
            (Vote.DOWNVOTE, 1, -1, -1),
        ],
    )
    def test_voting_first_time(
        self,
        authed_api_client,
        vote_value,
        expected_votes_count,
        expected_post_rating,
        expected_post_user_rating,
    ):
        client = authed_api_client(self.voter)
        result = self._vote_for_post(client, self.post, vote_value)
        self.post.refresh_from_db()

        expected_post_rating = self.post_original_rating + expected_post_rating
        expected_post_user_rating = (
            self.author_original_rating + expected_post_user_rating
        )
        assert self.post.user.rating == expected_post_user_rating

        assert result.data == {
            "slug": self.post.slug,
            "votes_up_count": self.post_original_votes_up_count + 1
            if vote_value == 1
            else self.post_original_votes_up_count,
            "votes_down_count": self.post_original_votes_down_count + 1
            if vote_value == -1
            else self.post_original_votes_down_count,
            "rating": expected_post_rating,
        }

    @pytest.mark.parametrize("vote_value", (Vote.UPVOTE, Vote.DOWNVOTE))
    def test_voting_for_own_post(self, authed_api_client, vote_value):
        client = authed_api_client(self.post.user)
        result = self._vote_for_post(client, self.post, vote_value)
        assert result.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("vote_value", (Vote.UPVOTE, Vote.DOWNVOTE))
    def test_double_vote(self, authed_api_client, vote_value):
        PostVoteFactory(post=self.post, user=self.post.user, value=vote_value)
        client = authed_api_client(self.post.user)
        result = self._vote_for_post(client, self.post, vote_value)
        assert result.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("vote_value", (Vote.UPVOTE, Vote.DOWNVOTE))
    def test_undo_vote(self, authed_api_client, vote_value):
        undo_value_mapping = {
            Vote.UPVOTE: Vote.DOWNVOTE,
            Vote.DOWNVOTE: Vote.UPVOTE,
        }
        client = authed_api_client(self.voter)
        self._vote_for_post(client, self.post, vote_value)
        result = self._vote_for_post(client, self.post, undo_value_mapping[vote_value])

        assert result.data == {
            "slug": self.post.slug,
            "votes_up_count": self.post_original_votes_up_count,
            "votes_down_count": self.post_original_votes_down_count,
            "rating": self.post_original_rating,
        }
        self.post.user.refresh_from_db()
        assert self.post.user.rating == self.author_original_rating

    def test_cant_vote_as_anonymous(self, anon_api_client):
        result = self._vote_for_post(anon_api_client(), self.post, Vote.UPVOTE)
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cant_vote_with_wrong_values(self, authed_api_client):
        client = authed_api_client(self.voter)
        result = self._vote_for_post(client, self.post, 10)
        assert result.status_code == status.HTTP_400_BAD_REQUEST

    def test_cant_vote_non_active(self, authed_api_client):
        voter = UserPublicFactory(is_active=False)
        client = authed_api_client(voter)
        result = self._vote_for_post(client, self.post, Vote.UPVOTE)
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def _vote_for_post(self, client, post, vote_value):
        return client.post(
            reverse("v1-api:posts:posts-vote", kwargs={"slug": post.slug}),
            data={"value": vote_value},
        )
