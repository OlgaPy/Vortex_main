import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from posts.choices import PostStatus
from posts.models import Post
from posts.tests.factories import PostFactory
from users.tests.factories import UserPublicFactory


@pytest.mark.django_db
class TestDeletePost:
    def setup(self):
        self.post = PostFactory(status=PostStatus.PUBLISHED)

    def test_anonymous_cant_delete_post(self, anon_api_client):
        result = self._delete_post(anon_api_client(), self.post)
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cant_delete_not_own_post(self, authed_api_client):
        user = UserPublicFactory()
        client = authed_api_client(user)
        result = self._delete_post(client, self.post)

        assert result.status_code == status.HTTP_404_NOT_FOUND
        post = Post.objects.filter(pk=self.post.pk).first()
        assert post.status == PostStatus.PUBLISHED

    def test_can_delete_own_post(self, authed_api_client):
        client = authed_api_client(self.post.user)
        result = self._delete_post(client, self.post)
        assert result.status_code == status.HTTP_204_NO_CONTENT
        assert Post.objects.filter(pk=self.post.pk).first().status == PostStatus.DELETED

    def _delete_post(self, client, post):
        return client.delete(
            reverse("v1-api:posts:my-posts-detail", kwargs={"slug": post.slug})
        )
