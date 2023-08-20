import uuid

from django.conf import settings
from drf_spectacular.utils import OpenApiParameter

INTERNAL_TOKEN = OpenApiParameter(
    name=settings.INTERNAL_TOKEN_HEADER,
    type=str,
    required=True,
    location=OpenApiParameter.HEADER,
    description=(
        "Token to authenticate requests coming from trusted source, like auth service"
    ),
)

POST_UUID = OpenApiParameter(
    name="post",
    type=uuid.UUID,
    required=True,
    location=OpenApiParameter.QUERY,
    description="UUID of the post to which comments are belongs.",
)
PARENT_COMMENT_UUID = OpenApiParameter(
    name="parent",
    type=uuid.UUID,
    required=False,
    location=OpenApiParameter.QUERY,
    description="UUID of the comment to fetch all children comments.",
)
