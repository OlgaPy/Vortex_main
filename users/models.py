from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from common.helpers import is_prod
from common.models import Timestamped
from users.choices import TagStatus, UserCommunityStatus, UserRelationStatus
from users.managers import KapibaraUserManager


class UserPublic(AbstractBaseUser, PermissionsMixin):
    """Information about user."""

    external_user_uid = models.CharField(max_length=36, unique=True, db_index=True)
    username = models.CharField(max_length=100, unique=True, db_index=True)
    email = models.EmailField(blank=True, default="")
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    bio = models.TextField(blank=True)
    rating = models.FloatField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    votes_up_count = models.PositiveIntegerField(default=0)
    votes_down_count = models.PositiveIntegerField(default=0)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    user_relation = models.ManyToManyField(
        to="self", through="users.UserRelation", blank=True
    )
    tags = models.ManyToManyField(to="posts.Tag", through="users.UserTag", blank=True)
    communities = models.ManyToManyField(
        "communities.Community", through="users.UserCommunity", blank=True
    )

    objects = KapibaraUserManager()

    USERNAME_FIELD = "username"

    def __str__(self):
        return f"<{self.pk}: {self.external_user_uid} / {self.username}>"

    def save(self, *args, **kwargs):
        """Save user and set password if passwort doesn't exist on non prod env."""
        if not self.password and not is_prod():
            self.password = make_password(settings.LOADTEST_PASSWORD)
        super().save(*args, **kwargs)


class UserTag(Timestamped):
    """List of tags which user either subscribed or ignored."""

    tag = models.ForeignKey("posts.Tag", on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    status = models.CharField(choices=TagStatus.choices, default=TagStatus.SUBSCRIBED)


class UserCommunity(Timestamped):
    """Communities user subscribed to or joined."""

    community = models.ForeignKey("communities.Community", on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    status = models.CharField(
        choices=UserCommunityStatus.choices, default=UserCommunityStatus.SUBSCRIBED
    )


class UserRelation(Timestamped):
    """Model to keep user relations, including subscriptions and ignored."""

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="+")
    related_user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="+"
    )
    status = models.CharField(
        choices=UserRelationStatus.choices, default=UserRelationStatus.SUBSCRIBED
    )
    active_until = models.DateField(blank=True, null=True)


class UserNote(Timestamped):
    """Model to keep user notes about particular user."""

    author = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="written_notes"
    )
    user_about = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="notes_about"
    )
    note = models.TextField()

    class Meta:
        unique_together = ("author", "user_about")
