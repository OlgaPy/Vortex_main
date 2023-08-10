from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint
from django_extensions.db.fields import AutoSlugField

from common.helpers import slugify_function
from common.models import Timestamped
from posts.choices import PostStatus, Vote


class PostGroup(Timestamped):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(
        populate_from=["name"],
        editable=True,
        slugify_function=slugify_function,
        allow_duplicates=False,
        db_index=True,
    )
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="post_groups"
    )

    def __str__(self):
        return self.name


class Post(Timestamped):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    post_group = models.ForeignKey(
        "posts.PostGroup", on_delete=models.SET_NULL, null=True, blank=True
    )
    community = models.ForeignKey(
        "communities.Community",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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
        max_length=9, choices=PostStatus.choices, default=PostStatus.PUBLISHED
    )
    publish_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        default_related_name = "posts"

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True)

    def __str__(self):
        return self.name


class PostVote(Timestamped):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=Vote.choices)

    class Meta:
        constraints = [
            UniqueConstraint(fields=("user", "post"), name="user_post_vote"),
        ]


class Comment(Timestamped):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="replies", null=True, blank=True
    )
    content = models.TextField()
    votes_up_count = models.IntegerField(default=0)
    votes_down_count = models.IntegerField(default=0)
    rating = models.IntegerField(default=0)


class CommentVote(Timestamped):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    value = models.IntegerField(choices=Vote.choices)

    class Meta:
        unique_together = ("user", "comment")
