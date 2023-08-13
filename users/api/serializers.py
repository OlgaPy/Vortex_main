from rest_framework import serializers

from users.models import UserPublic


class UserPublicFullSerializer(serializers.ModelSerializer):
    """Serializer to represent whole user info."""

    class Meta:
        model = UserPublic
        fields = (
            "username",
            "date_of_birth",
            "avatar",
            "bio",
            "rating",
            "comments_count",
            "votes_up_count",
            "votes_down_count",
        )
        read_only_fields = (
            "rating",
            "comments_count",
            "votes_up_count",
            "votes_down_count",
        )


class UserPublicMinimalSerializer(serializers.ModelSerializer):
    """Serializer to represent minimum info about user in posts."""

    class Meta:
        model = UserPublic
        fields = (
            "username",
            "avatar",
        )
