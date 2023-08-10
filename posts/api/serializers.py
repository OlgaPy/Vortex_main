from rest_framework import serializers

from common.api.fields import WritableSlugRelatedField
from posts.models import Post, PostVote, Tag


class PostSerializer(serializers.ModelSerializer):
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
            "created_at",
        )


class PostRatingOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "slug",
            "votes_up_count",
            "votes_down_count",
            "rating",
        )


class PostCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = WritableSlugRelatedField(
        slug_field="name", queryset=Tag.objects.all(), many=True, required=False
    )

    class Meta:
        model = Post
        fields = (
            "user",
            "title",
            "content",
            "tags",
        )


class PostVoteCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PostVote
        fields = (
            "user",
            "value",
        )
