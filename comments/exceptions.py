from rest_framework.exceptions import ValidationError


class CommentVoteException(ValidationError):
    """Raise exception when something goes wrong with casting vote."""


class CommentEditException(ValidationError):
    """Raise exception if comment can't be edited."""
