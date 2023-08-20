from mptt.querysets import TreeQuerySet

from comments.models import Comment
from users.models import UserPublic


def get_children_comments(
    comment: Comment, max_level: int = None
) -> TreeQuerySet[Comment]:
    children_qs = comment.get_children().select_related("user", "post")
    if max_level is not None:
        children_qs = children_qs.filter(level__lte=max_level)
    return children_qs


def get_user_default_comments_level(user: UserPublic) -> int:
    # TODO: implement this
    return 2
