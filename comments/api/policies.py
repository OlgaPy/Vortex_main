from django.conf import settings
from django.utils import timezone
from rest_access_policy import AccessPolicy, Statement


class CommentAccessPolicy(AccessPolicy):
    statements = [
        Statement(
            action=["list", "retrieve"],
            principal="*",
            effect="allow",
        ),
        Statement(
            action=["create"],
            principal="authenticated",
            effect="allow",
        ),
        Statement(
            action=["update", "partial_update"],
            principal="authenticated",
            effect="allow",
            condition=[
                "user_must_be_author",
                "should_not_have_ratings",
                "should_be_posted_not_before",
            ],
        ),
        Statement(
            action=["delete"],
            principal="*",
            effect="deny",
        ),
    ]

    def user_must_be_author(self, request, view, action):
        comment = view.get_object()
        return comment.user == request.user

    def should_not_have_ratings(self, request, view, action):
        comment = view.get_object()
        return not comment.votes.exists()

    def should_be_posted_not_before(self, request, view, action):
        comment = view.get_object()
        now = timezone.now()
        return (
            now - comment.created_at
        ).total_seconds() <= settings.COMMENTS_EDITABLE_WINDOW_MINUTES * 60
