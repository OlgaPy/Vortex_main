from django.conf import settings
from drf_spectacular.utils import OpenApiParameter

INTERNAL_TOKEN = OpenApiParameter(
    name=settings.INTERNAL_TOKEN_HEADER,
    type=str,
    required=True,
    location=OpenApiParameter.HEADER,
    description=(
        "Token to authenticate requests coming from trusted source, " "like auth service"
    ),
)
