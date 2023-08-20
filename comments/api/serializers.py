from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from comments.models import Comment
from comments.selectors import get_children_comments
from posts.models import Post
from users.api.serializers import UserPublicMinimalSerializer


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer to create comment."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    post = serializers.SlugRelatedField(slug_field="uuid", queryset=Post.objects.all())
    parent = serializers.SlugRelatedField(
        slug_field="uuid", queryset=Comment.objects.all(), required=False
    )

    class Meta:
        model = Comment
        fields = (
            "uuid",
            "user",
            "post",
            "parent",
            "content",
            "rating",
            "votes_up_count",
            "votes_down_count",
            "created_at",
        )

        read_only_fields = (
            "uuid",
            "rating",
            "votes_up_count",
            "votes_down_count",
            "created_at",
        )

    def validate(self, attrs):
        """Validate comment data, make sure parent comment from the same post."""
        if parent := attrs.get("parent"):
            post = attrs["post"]
            if parent.post_id != post.pk:
                raise ValidationError("Нельзя отвечать на комментарий из другого поста!")
        return super().validate(attrs)


class CommentSerializer(serializers.ModelSerializer):
    """Serializer to represent comment."""

    user = UserPublicMinimalSerializer()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "uuid",
            "user",
            "content",
            "rating",
            "votes_up_count",
            "votes_down_count",
            "created_at",
            "children",
        )
        read_only_fields = fields

    def get_children(self, obj: Comment):
        return CommentSerializer(
            get_children_comments(obj, max_level=self.context.get("max_level")),
            many=True,
            context=self.context,
        ).data
