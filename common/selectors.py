from django.conf import settings


def get_valid_internal_tokens() -> list[str]:
    """Fetch available internal tokens."""
    return settings.INTERNAL_TOKENS


def get_internal_token_from_request(request) -> str | None:
    """Fetch internal token from request if present."""
    return request.headers.get(settings.INTERNAL_TOKEN_HEADER)
