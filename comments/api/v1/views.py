from drf_spectacular.utils import extend_schema
from rest_framework import mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from comments.api.permissions import CommentPoster
from comments.api.serializers import CommentCreateSerializer, CommentSerializer
from comments.filters import CommentFilter
from comments.models import Comment
from common.api.parameters import POST_UUID


class CommentViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = Comment.objects.select_related("user", "post")
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated & CommentPoster,)
    lookup_field = "uuid"
    http_method_names = ["post", "get", "patch", "delete"]
    pagination_class = None
    filterset_class = CommentFilter

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return CommentCreateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]
        return super().get_permissions()

    @extend_schema(parameters=[POST_UUID])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        super().perform_create(serializer)
