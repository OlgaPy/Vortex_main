from django_filters import rest_framework as filters

from comments.models import Comment
from posts.models import Post


class CommentFilter(filters.FilterSet):
    post = filters.UUIDFilter(method="filter_by_post_uuid")
    parent = filters.UUIDFilter(method="filter_by_parent")

    def __init__(self, data=None, *args, **kwargs):
        method = getattr(kwargs.get("request"), "method", None)
        if method in ("PATCH", "DELETE"):
            return super().__init__(data, *args, **kwargs)
        if data is not None:
            data = data.copy()
            if not data.get("post"):
                # Just dummy UUID in order to return guaranteed empty queryset in case
                # post GET parameter not set
                data["post"] = "00000000-0000-0000-0000-000000000000"
        super().__init__(data, *args, **kwargs)

    def filter_by_post_uuid(self, queryset, name, value):
        """Find post by provided uuid and then filter by post id."""
        try:
            post = Post.objects.get(uuid=value)
        except Post.DoesNotExist:
            return queryset.none()
        return queryset.filter(post_id=post.pk)

    def filter_by_parent(self, queryset, name, value):
        try:
            parent = Comment.objects.get(uuid=value)
        except Comment.DoesNotExist:
            return queryset.none()

        return parent.get_children()
