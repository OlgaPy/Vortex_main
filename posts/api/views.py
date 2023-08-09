from rest_framework.viewsets import ModelViewSet

from posts.api.serializers import PostSerializer, PostCreateSerializer
from posts.choices import PostStatus
from posts.models import Post


class PostViewSet(ModelViewSet):
    queryset = Post.objects.filter(status=PostStatus.PUBLISHED)
    serializer_class = PostSerializer

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return PostCreateSerializer
        return self.serializer_class
