from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from common.api import parameters
from users.api.permissions import Authenticator, LoadtestWorker, OwnUser
from users.api.serializers import UserPublicCreateSerializer, UserPublicFullSerializer
from users.models import UserPublic
from users.services import activate_user_account, deactivate_user_account


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
    http_method_names = ["post", "get", "delete", "patch"]
    permission_classes = [Authenticator | LoadtestWorker]

    def get_permissions(self):
        """Return proper permissions based on action user performing."""
        if self.action in ("create", "activate", "deactivate"):
            permission = Authenticator | LoadtestWorker
            return [permission()]
        elif self.action in ("update", "partial_update"):
            permission = Authenticator | LoadtestWorker | OwnUser
            return [permission()]
        return [AllowAny()]

    def get_serializer_class(self):
        """Return serializer class based on action."""
        if self.action == "create":
            return UserPublicCreateSerializer
        return self.serializer_class

    @extend_schema(parameters=[parameters.INTERNAL_TOKEN])
    def create(self, request, *args, **kwargs):
        """Create UserPublic entry, accepting only internal call."""
        return super().create(request, *args, **kwargs)

    @extend_schema(parameters=[parameters.INTERNAL_TOKEN])
    @action(methods=["POST"], detail=True, serializer_class=UserPublicCreateSerializer)
    def activate(self, request, *args, **kwargs):
        """Activate user."""
        user = self.get_object()
        user = activate_user_account(user)
        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)

    @extend_schema(parameters=[parameters.INTERNAL_TOKEN])
    @action(methods=["POST"], detail=True, serializer_class=UserPublicCreateSerializer)
    def deactivate(self, request, *args, **kwargs):
        """Deactivate user."""
        user = self.get_object()
        user = deactivate_user_account(user)
        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)
