from rest_access_policy import AccessPolicy, Statement

from posts.selectors import can_edit_post


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
                "should_be_allowed_to_edit",
            ],
        ),
    ]

    def user_must_be_author(self, request, view, action):
        entity = view.get_object()
        return entity.user == request.user

    def should_be_allowed_to_edit(self, request, view, action):
        return can_edit_post(request.user, view.get_object())
