import uuid

from django.contrib.auth import get_user_model
from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from comments.choices import CommentVote
from common.models import Timestamped


class Comment(MPTTModel, Timestamped):
    """Model to store user comment on posts."""

    uuid = models.UUIDField(
        default=uuid.uuid4, unique=True, db_index=True, editable=False
    )
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    post = models.ForeignKey(
        "posts.Post", on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
    votes_up_count = models.IntegerField(default=0)
    votes_down_count = models.IntegerField(default=0)
    rating = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    class MPTTMeta:
        order_insertion_by = ["created_at"]

    def __str__(self):
        return f"<{self.pk}: {self.user.username} -> {self.post.title}>"


class CommentVote(Timestamped):
    """Model to store comment votes."""

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    comment = models.ForeignKey("comments.Comment", on_delete=models.CASCADE)
    value = models.IntegerField(choices=CommentVote.choices)

    class Meta:
        unique_together = ("user", "comment")
