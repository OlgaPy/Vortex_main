from rest_framework import serializers

from common.api.fields import WritableSlugRelatedField
from posts.models import Post, PostVote, Tag


class PostSerializer(serializers.ModelSerializer):
    """Serializer to represent Post instance."""

    tags = serializers.SlugRelatedField("name", many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "user",
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
            "created_at",
        )


class PostRatingOnlySerializer(serializers.ModelSerializer):
    """Serializer to return only rating related data."""

    class Meta:
        model = Post
        fields = (
            "slug",
            "votes_up_count",
            "votes_down_count",
            "rating",
        )


class PostCreateSerializer(serializers.ModelSerializer):
    """serializer to accept and validate data submitted as a post vote."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = WritableSlugRelatedField(
        slug_field="name", queryset=Tag.objects.all(), many=True, required=False
    )

    class Meta:
        model = Post
        fields = (
            "user",
            "title",
            "slug",
            "content",
            "tags",
            "status",
        )
        read_only_fields = ["slug", "status"]


class PostVoteCreateSerializer(serializers.ModelSerializer):
    """Serializer validating data submitted to cast a vote on a post."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PostVote
        fields = (
            "user",
            "value",
        )
