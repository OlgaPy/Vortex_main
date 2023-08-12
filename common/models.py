from django.db import models


class Timestamped(models.Model):
    """Abstract model to be inherited by model classes to have times or create/update."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
