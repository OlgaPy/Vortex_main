from django.db import models


class TagStatus(models.TextChoices):
    SUBSCRIBED = "S", "Subscribed"
    IGNORED = "I", "Ignored"


class UserCommunityStatus(models.TextChoices):
    SUBSCRIBED = "S", "Subscribed"
    JOINED = "J", "Joined"


class UserRelationStatus(models.TextChoices):
    SUBSCRIBED = "F", "Followed"
    BLOCKED = "B", "Blocked"
