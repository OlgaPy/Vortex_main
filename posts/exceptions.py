from rest_framework.exceptions import ValidationError


class PostVoteException(ValidationError):
    ...


class PostPublishException(ValidationError):
    ...


class PostDeleteException(ValidationError):
    ...
