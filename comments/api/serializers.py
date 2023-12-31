from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from comments.models import Comment, CommentVote
from comments.selectors import can_edit_comment, get_children_comments
from posts.models import Post
from users.api.serializers import UserPublicMinimalSerializer


class CommentSerializer(serializers.ModelSerializer):
    """Serializer to represent comment."""

    author = UserPublicMinimalSerializer(source="user")
    children = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "uuid",
            "author",
            "content",
            "rating",
            "votes_up_count",
            "votes_down_count",
            "created_at",
            "level",
            "children",
            "can_edit",
        )
        read_only_fields = fields

    def get_children(self, obj: Comment):
        return CommentSerializer(
            get_children_comments(obj, max_level=self.context.get("max_level")),
            many=True,
            context=self.context,
        ).data

    def get_can_edit(self, obj: Comment):
        request = self.context.get("request")
        user = request and request.user
        return can_edit_comment(user, obj)


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer to create comment."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    author = UserPublicMinimalSerializer(source="user", read_only=True)
    post = serializers.SlugRelatedField(
        slug_field="uuid", queryset=Post.objects.only("pk")
    )
    parent = serializers.SlugRelatedField(
        slug_field="uuid", queryset=Comment.objects.only("pk"), required=False
    )

    class Meta:
        model = Comment
        fields = (
            "uuid",
            "user",
            "author",
            "post",
            "parent",
            "content",
        )

        read_only_fields = (
            "uuid",
            "author",
        )

    def validate(self, attrs):
        """Validate comment data, make sure parent comment from the same post."""
        if parent := attrs.get("parent"):
            post = attrs["post"]
            if parent.post_id != post.pk:
                raise ValidationError("Нельзя отвечать на комментарий из другого поста!")
        return super().validate(attrs)


class CommentUpdateSerializer(serializers.ModelSerializer):
    author = UserPublicMinimalSerializer(source="user", read_only=True)

    class Meta:
        model = Comment
        fields = (
            "uuid",
            "author",
            "content",
        )

        read_only_fields = (
            "uuid",
            "author",
        )


class CommentVoteCreateSerializer(serializers.ModelSerializer):
    """Serializer validating data submitted to cast a vote on a comment."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CommentVote
        fields = (
            "user",
            "value",
        )


class CommentRatingOnlySerializer(serializers.ModelSerializer):
    """Serializer to return only rating related data."""

    class Meta:
        model = Comment
        fields = (
            "uuid",
            "votes_up_count",
            "votes_down_count",
            "rating",
        )
