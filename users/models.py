from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django_extensions.db.fields import AutoSlugField

from common.helpers import slugify_function
from common.models import Timestamped
from users.managers import KapibaraUserManager


class UserPublic(AbstractBaseUser, PermissionsMixin):
    external_user_uid = models.CharField(max_length=32, unique=True, db_index=True)
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    bio = models.TextField(blank=True)
    rating = models.FloatField(default=0)
    followers = models.ManyToManyField(
        "self", related_name="following", symmetrical=False
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    communities = models.ManyToManyField("users.Community", related_name="users")
    followed_users = models.ManyToManyField("self", blank=True)
    blocked_users = models.ManyToManyField(
        "self", related_name="blocking_users", blank=True
    )
    subscribed_tags = models.ManyToManyField(
        "posts.Tag", related_name="subscribed_users", blank=True
    )
    excluded_tags = models.ManyToManyField(
        "posts.Tag", related_name="users_with_excluded", blank=True
    )
    joined_communities = models.ManyToManyField(
        "users.Community", related_name="members", blank=True
    )
    subscribed_communities = models.ManyToManyField(
        "users.Community", related_name="subscribers", blank=True
    )

    objects = KapibaraUserManager()

    USERNAME_FIELD = "external_user_uid"


class Community(Timestamped):
    class Status(models.TextChoices):
        OPEN = "O", "Open"
        CLOSED = "C", "Closed"

    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(
        populate_from=["name"],
        editable=True,
        slugify_function=slugify_function,
        allow_duplicates=False,
        db_index=True,
    )
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_communities",
    )
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.OPEN)


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
