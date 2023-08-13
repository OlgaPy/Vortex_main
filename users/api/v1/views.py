from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from users.api.permissions import Authenticator, OwnUser
from users.api.serializers import UserPublicFullSerializer
from users.models import UserPublic


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """API to manage user profile."""

    queryset = UserPublic.objects.all()
    serializer_class = UserPublicFullSerializer
    lookup_field = "external_user_uid"
    http_method_names = ["post", "get", "patch", "delete"]

    def get_permissions(self):
        """Return proper permissions based on action user performing."""
        if self.action == "create":
            return [Authenticator()]
        elif self.action in ("update", "partial_update"):
            return [OwnUser()]
        return [AllowAny()]
