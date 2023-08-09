from rest_framework import serializers

from posts.models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "user",
            "title",
            "slug",
            "content",
            "post_group",
            "community",
            "views_count",
            "comments_count",
            "votes_up_count",
            "votes_down_count",
            "rating",
        )


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "title",
            "content",
            "tags",
        )
