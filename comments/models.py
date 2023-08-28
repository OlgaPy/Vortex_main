import uuid

from django.db import models
from django.db.models import UniqueConstraint
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from comments.choices import Vote
from common.models import Timestamped


class Comment(MPTTModel, Timestamped):
    """Model to store user comment on posts."""

    uuid = models.UUIDField(
        default=uuid.uuid4, unique=True, db_index=True, editable=False
    )
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    user = models.ForeignKey(
        "users.UserPublic", on_delete=models.CASCADE, related_name="comments"
    )
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

    def __str__(self):
        return f"<{self.pk}: {self.user.username} -> {self.post.title}>"


class CommentVote(Timestamped):
    """Model to store comment votes."""

    user = models.ForeignKey(
        "users.UserPublic", related_name="comment_votes", on_delete=models.CASCADE
    )
    comment = models.ForeignKey(
        "comments.Comment", related_name="votes", on_delete=models.CASCADE
    )
    value = models.SmallIntegerField(choices=Vote.choices)

    class Meta:
        constraints = [
            UniqueConstraint(fields=("user", "comment"), name="user_comment_vote"),
        ]
