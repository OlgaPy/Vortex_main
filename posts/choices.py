from django.db import models


class PostStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    DELETED = "deleted", "Deleted"


class Vote(models.IntegerChoices):
    UPVOTE = 1
    DOWNVOTE = -1
