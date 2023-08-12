import json

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from posts.tests.factories import PostFactory
from users.tests.factories import UserPublicFactory


@pytest.mark.django_db
class TestCreatePost:
    def setup(self):
        self.title = "Заголовок"
        self.expected_slug = "zagolovok"
        self.tags = ["тест", "проверка", "проверка"]
        self.content = [{"type": "header", "content": "Тест создания поста"}]
        self.data = {
            "title": self.title,
            "content": json.dumps(self.content),
            "tags": self.tags,
        }
        self.user = UserPublicFactory()

    def test_active_user_can_create_new_post(self, authed_api_client):
        result = self._create_post(authed_api_client(self.user), data=self.data)

        assert result.status_code == status.HTTP_201_CREATED
        data = result.data
        assert data["title"] == self.title
        assert data["content"] == self.content
        assert data["slug"] == self.expected_slug
        assert sorted(data["tags"]) == sorted(list(set(self.tags)))

    def test_not_active_user_cant_create_new_post(self, authed_api_client):
        result = self._create_post(authed_api_client(self.user), data=self.data)

        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def test_not_logged_in_user_cant_create_new_post(self, anon_api_client):
        result = self._create_post(anon_api_client(), data=self.data)

        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize("empty_field", ("title", "content"))
    def test_need_required_data_to_create_post(self, authed_api_client, empty_field):
        data = self.data.copy()
        data[empty_field] = ""
        result = self._create_post(authed_api_client(self.user), data=data)

        assert result.status_code == status.HTTP_400_BAD_REQUEST

    def test_can_edit_own_post(self, authed_api_client):
        post = PostFactory(user=self.user)
        title = "edited post"
        tags = ["new tag", "one more"]
        content = [{"edited": "post"}]
        result = self._edit_post(
            authed_api_client(self.user),
            post.slug,
            {"title": title, "tags": tags, "content": json.dumps(content)},
        )

        assert result.status_code == status.HTTP_200_OK
        data = result.data
        assert data["title"] == title
        assert data["slug"] == self.expected_slug
        assert sorted(data["tags"]) == sorted(tags)
        assert data["content"] == content

    def test_cannot_edit_not_own_post(self, authed_api_client):
        post = PostFactory()
        result = self._edit_post(
            authed_api_client(self.user), post.slug, {"title": "test"}
        )
        assert result.status_code == status.HTTP_404_NOT_FOUND

    def test_cannot_edit_as_not_logged_in_user(self, anon_api_client):
        post = PostFactory()
        result = self._edit_post(anon_api_client(), post.slug, {"title": "test"})
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_edit_as_not_active_user(self, authed_api_client):
        post = PostFactory(user=UserPublicFactory(is_active=False))
        result = self._edit_post(
            authed_api_client(post.user), post.slug, {"title": "test"}
        )
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def _create_post(self, client, data):
        return client.post(reverse("v1-api:posts:my-posts-list"), data=data)

    def _edit_post(self, client, slug, data):
        return client.patch(
            reverse("v1-api:posts:my-posts-detail", kwargs={"slug": slug}), data=data
        )
