from rest_framework.exceptions import ValidationError


class PostVoteException(ValidationError):
    """Raise exception when something goes wrong with casting vote."""


class PostPublishException(ValidationError):
    """Raise exception when something goes wrong when publishing post."""


class PostDeleteException(ValidationError):
    """Raise exception when something goes wrong with post deletion."""
