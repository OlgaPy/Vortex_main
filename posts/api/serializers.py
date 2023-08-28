from rest_framework import serializers

from common.api.fields import WritableSlugRelatedField
from posts.models import Post, PostVote, Tag
from users.api.serializers import UserPublicMinimalSerializer


class PostSerializer(serializers.ModelSerializer):
    """Serializer to represent Post instance."""

    author = UserPublicMinimalSerializer(source="user")
    tags = serializers.SlugRelatedField("name", many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "uuid",
            "author",
            "title",
            "slug",
            "content",
            "post_group",
            "community",
            "tags",
            "views_count",
            "comments_count",
            "votes_up_count",
            "votes_down_count",
            "rating",
            "status",
            "published_at",
        )


class PostRatingOnlySerializer(serializers.ModelSerializer):
    """Serializer to return only rating related data."""

    class Meta:
        model = Post
        fields = (
            "uuid",
            "slug",
            "votes_up_count",
            "votes_down_count",
            "rating",
        )


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer to accept and validate data to create Post."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    author = UserPublicMinimalSerializer(source="user", read_only=True)
    tags = WritableSlugRelatedField(
        slug_field="name", queryset=Tag.objects.all(), many=True, required=False
    )

    class Meta:
        model = Post
        fields = (
            "uuid",
            "user",
            "author",
            "title",
            "slug",
            "content",
            "tags",
            "status",
        )
        read_only_fields = (
            "uuid",
            "author",
            "slug",
            "status",
        )


class PostVoteCreateSerializer(serializers.ModelSerializer):
    """Serializer validating data submitted to cast a vote on a post."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PostVote
        fields = (
            "user",
            "value",
        )
