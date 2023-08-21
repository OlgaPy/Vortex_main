import datetime

import pytest
from django.utils import timezone
from freezegun import freeze_time
from funcy import first
from rest_framework import status
from rest_framework.reverse import reverse

from comments.tests.factories import CommentFactory, VoteFactory
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

    def test_can_reply_to_comment(self, authed_api_client):
        content = "test comment"
        root_comment = CommentFactory(post=self.post)
        result = self._post_comment(
            authed_api_client(self.user),
            self.post,
            data={
                "content": content,
                "parent": root_comment.uuid,
            },
        )
        root_comment.refresh_from_db()
        data = result.data
        assert result.status_code == status.HTTP_201_CREATED
        assert self.post.comments.count() == 2
        child_comment = first(root_comment.get_children())

        assert data["uuid"] == str(child_comment.uuid)

    def test_can_edit_comment(self, authed_api_client):
        comment = CommentFactory(post=self.post)
        new_content = "edited comment"
        result = self._edit_comment(
            authed_api_client(comment.user), comment, data={"content": new_content}
        )

        assert result.status_code == status.HTTP_200_OK
        data = result.data
        comment.refresh_from_db()
        assert data["content"] == new_content
        assert comment.content == new_content

    def test_cannot_edit_not_own_comment(self, authed_api_client):
        comment = CommentFactory(post=self.post)
        result = self._edit_comment(
            authed_api_client(self.user), comment, data={"content": "new content"}
        )

        assert result.status_code == status.HTTP_403_FORBIDDEN

    def test_not_logged_in_cannot_edit_comment(self, anon_api_client):
        result = self._edit_comment(
            anon_api_client(), CommentFactory(), data={"content": "new content"}
        )
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_edit_comment_with_ratings(self, authed_api_client):
        comment = CommentFactory(post=self.post)
        VoteFactory(comment=comment)
        result = self._edit_comment(
            authed_api_client(comment.user), comment, data={"content": "edited comment"}
        )

        assert result.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_edit_comment_after_specific_time(self, authed_api_client, settings):
        minutes = 1
        settings.COMMENTS_EDITABLE_WINDOW_MINUTES = minutes
        comment = CommentFactory(post=self.post)
        now = timezone.now()
        with freeze_time(now + datetime.timedelta(minutes=minutes + 1)):
            result = self._edit_comment(
                authed_api_client(comment.user),
                comment,
                data={"content": "edited comment"},
            )

        assert result.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_delete_comment(self, authed_api_client):
        result = self._delete_comment(
            authed_api_client(self.user),
            CommentFactory(user=self.user),
        )
        assert result.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.skip
    def test_need_post_uuid_param_to_fetch_comments(self):
        assert False

    @pytest.mark.skip
    def test_can_get_children_comments_up_to_level(self):
        assert False

    def _post_comment(self, client, post, data):
        data["post"] = post.uuid
        return client.post(reverse("v1:comments:comments-list"), data=data)

    def _edit_comment(self, client, comment, data):
        return client.patch(
            reverse("v1:comments:comments-detail", kwargs={"uuid": comment.uuid}),
            data=data,
        )

    def _delete_comment(self, client, comment):
        return client.delete(
            reverse("v1:comments:comments-detail", kwargs={"uuid": comment.uuid}),
        )
