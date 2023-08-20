from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from comments.models import Comment
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
            "rating",
            "votes_up_count",
            "votes_down_count",
            "created_at",
        )

    def validate(self, attrs):
        """Validate comment data, make sure parent comment from the same post."""
        if parent := attrs.get("parent"):
            post = attrs["post"]
            if parent.pk != post.pk:
                raise ValidationError("Нельзя отвечать на комментарий из другого поста!")
        return super().validate(attrs)


class CommentSerializer(serializers.ModelSerializer):
    """Serializer to represent comment."""

    user = UserPublicMinimalSerializer()

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
        )
        read_only_fields = fields
