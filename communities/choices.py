from django.db import models


class CommunityStatus(models.TextChoices):
    OPEN = "O", "Open"
    CLOSED = "C", "Closed"
