from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from common.models import Timestamped
from users.choices import TagStatus, UserCommunityStatus, UserRelationStatus
from users.managers import KapibaraUserManager


class UserPublic(AbstractBaseUser, PermissionsMixin):
    external_user_uid = models.CharField(max_length=32, unique=True, db_index=True)
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    bio = models.TextField(blank=True)
    rating = models.FloatField(default=0)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    communities = models.ManyToManyField(
        "users.Community", related_name="users", blank=True
    )
    user_relation = models.ManyToManyField(
        to="self", through="users.UserRelation", blank=True
    )
    tags = models.ManyToManyField(to="posts.Tag", through="users.UserTag", blank=True)
    communities = models.ManyToManyField(
        "communities.Community", through="users.UserCommunity", blank=True
    )

    objects = KapibaraUserManager()

    USERNAME_FIELD = "external_user_uid"


class UserTag(Timestamped):
    tag = models.ForeignKey("posts.Tag", on_delete=models.CASCADE)
    user = models.ForeignKey("users.UserPublic", on_delete=models.CASCADE)
    status = models.CharField(choices=TagStatus.choices, default=TagStatus.SUBSCRIBED)


class UserCommunity(Timestamped):
    community = models.ForeignKey("communities.Community", on_delete=models.CASCADE)
    user = models.ForeignKey("users.UserPublic", on_delete=models.CASCADE)
    status = models.CharField(
        choices=UserCommunityStatus.choices, default=UserCommunityStatus.SUBSCRIBED
    )


class UserRelation(Timestamped):
    user = models.ForeignKey("users.UserPublic", on_delete=models.CASCADE)
    related_user = models.ForeignKey("users.UserPublic", on_delete=models.CASCADE)
    status = models.CharField(
        choices=UserRelationStatus.choices, default=UserRelationStatus.SUBSCRIBED
    )
    active_until = models.DateField(blank=True, null=True)


class UserNote(Timestamped):
    author = models.ForeignKey(
        "users.UserPublic", on_delete=models.CASCADE, related_name="written_notes"
    )
    user_about = models.ForeignKey(
        "users.UserPublic", on_delete=models.CASCADE, related_name="notes_about"
    )
    note = models.TextField()

    class Meta:
        unique_together = ("author", "user_about")
