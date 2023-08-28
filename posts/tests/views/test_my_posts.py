import datetime
import json

import pytest
from django.utils import timezone
from freezegun import freeze_time
from funcy import first
from rest_framework import status
from rest_framework.reverse import reverse

from posts.choices import PostStatus
from posts.tests.factories import PostFactory
from users.tests.factories import UserPublicFactory


@pytest.mark.django_db
class TestMyPosts:
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
        result = self._create_post(
            authed_api_client(UserPublicFactory(is_active=False)), data=self.data
        )

        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def test_not_logged_in_user_cant_create_new_post(self, anon_api_client):
        result = self._create_post(anon_api_client(), data=self.data)

        assert result.status_code == status.HTTP_401_UNAUTHORIZED, result.content.decode()

    def test_not_logged_in_user_cant_fetch_my_posts(self, anon_api_client):
        result = self._fetch_my_posts(anon_api_client())
        assert result.status_code == status.HTTP_401_UNAUTHORIZED, result.content.decode()

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
            post.uuid,
            {"title": title, "tags": tags, "content": json.dumps(content)},
        )

        assert result.status_code == status.HTTP_200_OK, result.content.decode()
        data = result.data
        assert data["title"] == title
        assert sorted(data["tags"]) == sorted(tags)
        assert data["content"] == content

    def test_cannot_edit_not_own_post(self, authed_api_client):
        post = PostFactory()
        result = self._edit_post(
            authed_api_client(self.user), post.uuid, {"title": "test"}
        )
        assert result.status_code == status.HTTP_404_NOT_FOUND

    def test_cannot_edit_as_not_logged_in_user(self, anon_api_client):
        post = PostFactory()
        result = self._edit_post(anon_api_client(), post.uuid, {"title": "test"})
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_edit_as_not_active_user(self, authed_api_client):
        post = PostFactory(user=UserPublicFactory(is_active=False))
        result = self._edit_post(
            authed_api_client(post.user), post.uuid, {"title": "test"}
        )
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def test_can_list_own_posts(self, authed_api_client):
        my_post = PostFactory(status=PostStatus.PUBLISHED)
        PostFactory(status=PostStatus.PUBLISHED)

        result = self._fetch_my_posts(client=authed_api_client(my_post.user))

        assert result.status_code == status.HTTP_200_OK, result.content.decode()

        data = result.data
        assert len(data["results"]) == 1
        post = first(data["results"])
        assert post["uuid"] == str(my_post.uuid)

    def test_cant_publish_not_own_post(self, authed_api_client):
        post = PostFactory(status=PostStatus.DRAFT)
        user = UserPublicFactory()

        client = authed_api_client(user)

        result = self._publish_post(client, post)

        assert result.status_code == status.HTTP_404_NOT_FOUND, result.content.decode()

    @pytest.mark.parametrize(
        "original_status,expected_status_code",
        (
            (PostStatus.DRAFT, status.HTTP_200_OK),
            (PostStatus.PUBLISHED, status.HTTP_200_OK),
            (PostStatus.DELETED, status.HTTP_400_BAD_REQUEST),
        ),
    )
    @freeze_time(datetime.datetime(2023, 8, 28, 10, 0, 0))
    def test_can_publish_certain_statuses(
        self, authed_api_client, original_status, expected_status_code, settings
    ):
        post = PostFactory(status=original_status)
        client = authed_api_client(post.user)
        result = self._publish_post(client, post)
        assert result.status_code == expected_status_code, result.content.decode()
        if expected_status_code != status.HTTP_400_BAD_REQUEST:
            post.refresh_from_db()
            now = timezone.now()
            assert result.data["status"] == PostStatus.PUBLISHED
            if original_status == PostStatus.DRAFT:
                assert result.data["published_at"] == now.strftime(
                    settings.REST_FRAMEWORK["DATETIME_FORMAT"]
                )

    @pytest.mark.parametrize(
        "post_status,expected_status_code",
        (
            (PostStatus.DRAFT, status.HTTP_200_OK),
            (PostStatus.PUBLISHED, status.HTTP_403_FORBIDDEN),
        ),
    )
    def test_edit_post_after_specific_time(
        self, post_status, expected_status_code, authed_api_client, settings
    ):
        minutes = 1
        settings.POSTS_EDITABLE_WINDOW_MINUTES = minutes
        post = PostFactory(status=post_status, published_at=timezone.now())
        now = timezone.now()
        with freeze_time(now + datetime.timedelta(minutes=minutes + 1)):
            result = self._edit_post(
                authed_api_client(post.user),
                post.uuid,
                data={"title": "new title"},
            )

        assert result.status_code == expected_status_code, result.content.decode()

    def _fetch_my_posts(self, client):
        return client.get(reverse("v1:posts:my-posts-list"))

    def _publish_post(self, client, post):
        return client.post(
            reverse("v1:posts:my-posts-publish", kwargs={"uuid": post.uuid})
        )

    def _create_post(self, client, data):
        return client.post(reverse("v1:posts:my-posts-list"), data=data)

    def _edit_post(self, client, uuid, data):
        return client.patch(
            reverse("v1:posts:my-posts-detail", kwargs={"uuid": uuid}), data=data
        )
