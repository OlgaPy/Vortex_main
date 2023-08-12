from django.contrib.auth import get_user_model
from django.db import models
from django_extensions.db.fields import AutoSlugField

from common.helpers import slugify_function
from common.models import Timestamped
from communities.choices import CommunityStatus


class Community(Timestamped):
    """Model for communities."""

    name = models.CharField(max_length=100, unique=True)
    avatar = models.ImageField(upload_to="community/images/", null=True, blank=True)
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
    status = models.CharField(
        max_length=1, choices=CommunityStatus.choices, default=CommunityStatus.OPEN
    )
