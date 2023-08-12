import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from posts.choices import PostStatus
from posts.tests.factories import PostFactory
from users.tests.factories import UserPublicFactory


@pytest.mark.django_db
class TestMakePostPublished:
    def test_cant_publish_not_own_post(self, authed_api_client):
        post = PostFactory(status=PostStatus.DRAFT)
        user = UserPublicFactory()

        client = authed_api_client(user)

        result = self._publish_post(client, post)

        assert result.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        "original_status,expected_status_code",
        (
            (PostStatus.DRAFT, status.HTTP_200_OK),
            (PostStatus.PUBLISHED, status.HTTP_200_OK),
            (PostStatus.DELETED, status.HTTP_400_BAD_REQUEST),
        ),
    )
    def test_can_publish_certain_statuses(
        self, authed_api_client, original_status, expected_status_code
    ):
        post = PostFactory(status=original_status)
        client = authed_api_client(post.user)
        result = self._publish_post(client, post)
        assert result.status_code == expected_status_code
        if expected_status_code != status.HTTP_400_BAD_REQUEST:
            assert result.data["status"] == PostStatus.PUBLISHED

    def _publish_post(self, client, post):
        return client.post(
            reverse("v1-api:posts:my-posts-publish", kwargs={"slug": post.slug})
        )
