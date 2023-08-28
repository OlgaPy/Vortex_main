from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from comments.api.policies import CommentAccessPolicy
from comments.api.serializers import (
    CommentCreateSerializer,
    CommentRatingOnlySerializer,
    CommentSerializer,
    CommentUpdateSerializer,
    CommentVoteCreateSerializer,
)
from comments.exceptions import CommentEditException
from comments.filters import CommentFilter
from comments.models import Comment
from comments.selectors import get_comments_root_nodes_qs, get_user_default_comments_level
from comments.services import (
    record_vote_for_comment,
    update_author_comments_count,
    update_post_comments_count,
)
from common.api.parameters import PARENT_COMMENT_UUID, POST_UUID


class CommentViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = get_comments_root_nodes_qs()
    serializer_class = CommentSerializer
    permission_classes = (CommentAccessPolicy,)
    lookup_field = "uuid"
    http_method_names = ["post", "get", "patch", "delete"]
    pagination_class = None
    filterset_class = CommentFilter

    def get_serializer_class(self):
        if self.action in ["create"]:
            return CommentCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return CommentUpdateSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        # FIXME: This need to move to selectors
        current_level = 0
        if comment := Comment.objects.filter(
            uuid=self.request.query_params.get("parent")
        ).first():
            current_level = comment.level

        context = super().get_serializer_context()
        context["max_level"] = current_level + get_user_default_comments_level(
            self.request.user
        )
        return context

    @extend_schema(parameters=[POST_UUID, PARENT_COMMENT_UUID])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        update_author_comments_count(serializer.instance)
        update_post_comments_count(serializer.instance)

    def perform_update(self, serializer):
        instance = serializer.instance
        if instance.votes.exists():
            raise CommentEditException(
                "Нельзя редактировать т.к. за этот комментарий уже проголосовали"
            )
        serializer.save()

    @action(
        methods=["POST"],
        detail=True,
        serializer_class=CommentVoteCreateSerializer,
    )
    def vote(self, request, *args, **kwargs):
        """Record vote for the comment."""
        comment = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record_vote_for_comment(comment, request.user, serializer.data["value"])
        comment.refresh_from_db()
        return Response(
            CommentRatingOnlySerializer(comment).data, status=status.HTTP_201_CREATED
        )
