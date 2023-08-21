import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from posts.tests.factories import PostFactory
from users.tests.factories import UserPublicFactory


@pytest.mark.django_db
class TestCommentViewSet:
    def setup(self):
        self.initial_post_comments_count = 5
        self.post = PostFactory(comments_count=self.initial_post_comments_count)
        self.initial_user_comments_count = 10
        self.user = UserPublicFactory(comments_count=self.initial_user_comments_count)

    def test_active_user_can_post_comment(self, authed_api_client):
        content = "test comment"
        result = self._post_comment(
            authed_api_client(self.user), self.post, {"content": content}
        )
        data = result.data
        assert result.status_code == status.HTTP_201_CREATED, result.content.decode()
        assert data["author"]["username"] == self.user.username
        assert data["content"] == content

        self.post.refresh_from_db()
        self.user.refresh_from_db()
        assert self.post.comments.count() == 1
        assert self.post.comments_count == self.initial_post_comments_count + 1
        assert self.user.comments_count == self.initial_user_comments_count + 1

    def test_not_active_user_cant_post_comment(self, authed_api_client):
        user = UserPublicFactory(is_active=False)
        result = self._post_comment(
            authed_api_client(user), self.post, {"content": "test"}
        )
        assert result.status_code == status.HTTP_401_UNAUTHORIZED, result.content.decode()
        assert self.post.comments.count() == 0

    def test_not_logged_in_user_cant_post_comment(self, anon_api_client):
        result = self._post_comment(anon_api_client(), self.post, {"content": "test"})
        assert result.status_code == status.HTTP_401_UNAUTHORIZED, result.content.decode()
        assert self.post.comments.count() == 0

    def test_can_reply_to_comment(self):
        assert False

    def test_can_edit_comment_with_no_replies(self):
        assert False

    def test_cannot_edit_comment_with_replies(self):
        assert False

    def test_cannot_edit_not_own_comment(self):
        assert False

    def test_cannot_delete_comment(self):
        assert False

    def test_need_post_uuid_param_to_fetch_comments(self):
        assert False

    def test_can_get_children_comments_up_to_level(self):
        assert False

    def _post_comment(self, client, post, data):
        data["post"] = post.uuid
        return client.post(reverse("v1:comments:comments-list"), data=data)
