from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from posts.api.serializers import (
    PostSerializer,
    PostCreateSerializer,
    PostVoteCreateSerializer,
    PostRatingOnlySerializer,
)
from posts.models import Post
from posts.permissions import Poster, PostVoter
from posts.selectors import fetch_new_posts, fetch_user_posts
from posts.services import record_vote_for_post, publish_post, delete_post


class MyPostsViewSet(ListModelMixin, GenericViewSet):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = "slug"
    lookup_field = "slug"

    def get_queryset(self):
        return fetch_user_posts(self.request.user)


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated & Poster,)
    lookup_url_kwarg = "slug"
    lookup_field = "slug"

    def get_queryset(self):
        if self.action in ("create", "update", "partial_update", "publish"):
            return fetch_user_posts(self.request.user)
        return fetch_new_posts()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return PostCreateSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in ("retrieve", "list"):
            return [AllowAny()]
        return super().get_permissions()

    @action(
        methods=["POST"],
        detail=True,
        serializer_class=PostVoteCreateSerializer,
        permission_classes=(IsAuthenticated & PostVoter,),
    )
    def vote(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record_vote_for_post(post, request.user, serializer.data["value"])
        post.refresh_from_db()

        return Response(
            PostRatingOnlySerializer(post).data, status=status.HTTP_201_CREATED
        )

    @action(
        methods=["POST"],
        detail=True,
    )
    def publish(self, request, *args, **kwargs):
        post = self.get_object()
        post = publish_post(post, request.user)
        return Response(PostSerializer(post).data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance: Post):
        delete_post(instance, self.request.user)
