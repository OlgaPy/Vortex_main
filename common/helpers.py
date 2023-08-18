from django.conf import settings
from slugify import CYRILLIC, Slugify

from common.selectors import get_internal_token_from_request, get_valid_internal_tokens


def slugify_function(text: str) -> str:
    """Slugify text, also works with cyrillic letters."""
    slugify = Slugify(pretranslate=CYRILLIC)
    return slugify(text).lower()


def is_prod() -> bool:
    """Check if running in production environment."""
    return settings.ENVIRONMENT == "production"


def is_request_signed_with_valid_internal_token(request) -> bool:
    """Check if request has valid internal token in headers."""
    token = get_internal_token_from_request(request)
    return token in get_valid_internal_tokens()
