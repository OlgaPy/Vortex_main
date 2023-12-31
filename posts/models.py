import uuid

from django.db import models
from django.db.models import UniqueConstraint
from django_extensions.db.fields import AutoSlugField

from common.helpers import slugify_function
from common.models import Timestamped
from posts.choices import PostStatus, Vote


class PostGroup(Timestamped):
    """Model to group posts into series."""

    name = models.CharField(max_length=100)
    slug = AutoSlugField(
        populate_from=["name"],
        editable=True,
        slugify_function=slugify_function,
        allow_duplicates=False,
        db_index=True,
    )
    user = models.ForeignKey(
        "users.UserPublic", on_delete=models.CASCADE, related_name="post_groups"
    )

    def __str__(self):
        return self.name


class Post(Timestamped):
    """Model represents Post entity."""

    uuid = models.UUIDField(
        default=uuid.uuid4, unique=True, db_index=True, editable=False
    )
    user = models.ForeignKey(
        "users.UserPublic", on_delete=models.CASCADE, related_name="posts"
    )
    post_group = models.ForeignKey(
        "posts.PostGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )
    community = models.ForeignKey(
        "communities.Community",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )
    title = models.CharField(max_length=200)
    slug = AutoSlugField(
        populate_from=["title"],
        editable=True,
        slugify_function=slugify_function,
        allow_duplicates=False,
        db_index=True,
    )
    # need to add JSON schema validation, expected format is:
    # [
    #   {
    #       "type": "header",
    #       "content": "header content"
    #   },
    #   {
    #       "type": "paragraph",
    #       "content": "content with some <b>allowed</b> <em>tags</em>"
    #   }
    # ]
    content = models.JSONField()
    image = models.ImageField(upload_to="posts/images/", null=True, blank=True)
    video = models.FileField(upload_to="posts/videos/", null=True, blank=True)
    tags = models.ManyToManyField("posts.Tag", blank=True)
    views_count = models.IntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    votes_up_count = models.PositiveIntegerField(default=0)
    votes_down_count = models.PositiveIntegerField(default=0)
    rating = models.IntegerField(default=0)
    status = models.CharField(
        max_length=9, choices=PostStatus.choices, default=PostStatus.DRAFT
    )
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"<{self.pk}: {self.title}>"


class Tag(models.Model):
    """Model to keep all created tags."""

    name = models.CharField(max_length=50, unique=True, db_index=True)

    def __str__(self):
        return self.name


class PostVote(Timestamped):
    """Model to store post votes."""

    user = models.ForeignKey("users.UserPublic", on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=Vote.choices)

    class Meta:
        constraints = [
            UniqueConstraint(fields=("user", "post"), name="user_post_vote"),
        ]
