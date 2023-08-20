from django_filters import rest_framework as filters

from posts.models import Post


class CommentFilter(filters.FilterSet):
    post = filters.UUIDFilter(method="filter_by_post_uuid")

    def __init__(self, data=None, *args, **kwargs):
        if data is not None:
            data = data.copy()
            if not data.get("post"):
                data["post"] = "00000000-0000-0000-0000-000000000000"
        super().__init__(data, *args, **kwargs)

    def filter_by_post_uuid(self, queryset, name, value):
        """Find post by provided uuid and then filter by post id."""
        try:
            post = Post.objects.get(uuid=value)
        except Post.DoesNotExist:
            return queryset.none()
        return queryset.filter(post_id=post.pk)
