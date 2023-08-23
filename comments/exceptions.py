from rest_framework.exceptions import ValidationError


class CommentVoteException(ValidationError):
    """Raise exception when something goes wrong with casting vote."""
