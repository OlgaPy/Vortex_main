import pytest

from posts.tests.factories import PostFactory


@pytest.mark.parametrize
class TestCommentViewSet:
    def setup(self):
        self.post = PostFactory()

    def test_active_user_can_post_comment(self):
        assert False

    def test_not_active_user_cant_post_comment(self):
        assert False

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
