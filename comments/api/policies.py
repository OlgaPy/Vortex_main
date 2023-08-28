from rest_access_policy import AccessPolicy, Statement

from comments.selectors import can_edit_comment


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
                "should_be_allowed_to_edit",
            ],
        ),
        Statement(
            action=["delete"],
            principal="*",
            effect="deny",
        ),
        Statement(
            action=["vote"],
            principal="authenticated",
            effect="allow",
        ),
    ]

    def user_must_be_author(self, request, view, action):
        comment = view.get_object()
        return comment.user == request.user

    def should_be_allowed_to_edit(self, request, view, action):
        return can_edit_comment(request.user, view.get_object())
