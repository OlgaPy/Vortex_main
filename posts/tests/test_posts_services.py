import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from posts.choices import PostStatus, Vote
from posts.models import PostVote
from posts.tests.factories import PostFactory, PostVoteFactory
from users.tests.factories import UserPublicFactory


@pytest.mark.django_db
class TestRecordVoteForPost:
    def setup(self):
        self.post_original_rating = 10
        self.post_original_votes_up_count = 20
        self.post_original_votes_down_count = -10
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
        result = client.post(
            reverse("api.posts:post-vote", kwargs={"slug": self.post.slug}),
            data={"value": vote_value},
        )
        self.post.refresh_from_db()

        assert PostVote.objects.filter(
            user=self.voter, post=self.post, value=vote_value
        ).exists()

        expected_post_rating = self.post_original_rating + expected_post_rating
        expected_post_user_rating = (
            self.author_original_rating + expected_post_user_rating
        )
        assert self.post.rating == expected_post_rating
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

    def test_voting_for_own_post(self, authed_api_client):
        client = authed_api_client(self.post.user)
        result = client.post(
            reverse("api.posts:post-vote", kwargs={"slug": self.post.slug}),
            data={"value": Vote.UPVOTE},
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("vote_value", (Vote.UPVOTE, Vote.DOWNVOTE))
    def test_double_vote(self, authed_api_client, vote_value):
        PostVoteFactory(post=self.post, user=self.post.user, value=vote_value)
        client = authed_api_client(self.post.user)
        result = client.post(
            reverse("api.posts:post-vote", kwargs={"slug": self.post.slug}),
            data={"value": vote_value},
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("existing_vote_value", (Vote.UPVOTE, Vote.DOWNVOTE))
    def test_undo_vote(self, authed_api_client, existing_vote_value):
        undo_value_mapping = {
            Vote.UPVOTE: Vote.DOWNVOTE,
            Vote.DOWNVOTE: Vote.UPVOTE,
        }
        client = authed_api_client(self.voter)
        client.post(
            reverse("api.posts:post-vote", kwargs={"slug": self.post.slug}),
            data={"value": existing_vote_value},
        )

        result = client.post(
            reverse("api.posts:post-vote", kwargs={"slug": self.post.slug}),
            data={"value": undo_value_mapping[existing_vote_value]},
        )
        assert result.data == {
            "slug": self.post.slug,
            "votes_up_count": self.post_original_votes_up_count,
            "votes_down_count": self.post_original_votes_down_count,
            "rating": self.post_original_rating,
        }
        self.post.user.refresh_from_db()
        assert self.post.user.rating == self.author_original_rating
