from django.utils import timezone
from rest_access_policy import AccessPolicy, Statement

from posts.choices import PostStatus
from posts.models import Post
from posts.selectors import get_post_editable_window_minutes


class OwnPostAccessPolicy(AccessPolicy):
    statements = [
        Statement(
            action=["list", "create"],
            principal="authenticated",
            effect="allow",
        ),
        Statement(
            action=["retrieve", "destroy", "publish"],
            principal="authenticated",
            effect="allow",
            condition=["user_must_be_author"],
        ),
        Statement(
            action=["update", "partial_update"],
            principal="authenticated",
            effect="allow",
            condition=[
                "user_must_be_author",
                "should_be_posted_not_before",
            ],
        ),
    ]

    def user_must_be_author(self, request, view, action):
        entity = view.get_object()
        return entity.user == request.user

    def should_be_posted_not_before(self, request, view, action):
        entity: Post = view.get_object()
        if entity.status != PostStatus.PUBLISHED:
            return True
        if not entity.published_at:
            return True
        now = timezone.now()
        return (
            now - entity.published_at
        ).total_seconds() <= get_post_editable_window_minutes() * 60
