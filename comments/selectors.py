from django.conf import settings
from django.utils import timezone
from mptt.querysets import TreeQuerySet

from comments.models import Comment, CommentVote
from users.models import UserPublic


def get_children_comments(
    comment: Comment, max_level: int = None
) -> TreeQuerySet[Comment]:
    children_qs = comment.get_children().select_related("user", "post")
    if max_level is not None:
        children_qs = children_qs.filter(level__lte=max_level)
    return children_qs


def get_user_default_comments_level(user: UserPublic) -> int:
    # TODO: implement this based on user settings
    return settings.COMMENTS_TREE_DEFAULT_LEVEL


def get_comments_root_nodes_qs() -> TreeQuerySet[Comment]:
    """Return comments root nodes queryset."""
    return (
        Comment.objects.root_nodes()
        .select_related("user", "post")
        .prefetch_related("votes")
        .order_by("created_at")
    )


def get_comment_editable_window_minutes() -> int:
    """Return for how many minutes since posting comment can be edited."""
    return settings.COMMENTS_EDITABLE_WINDOW_MINUTES


def get_comment_vote_value_for_author(
    author: UserPublic, comment_vote: CommentVote
) -> float:
    """Get value of how much rating comment author should get on a single comment vote."""
    return comment_vote.value * settings.COMMENT_RATING_MULTIPLIER


def can_edit_comment(user: UserPublic, comment: Comment) -> bool:
    if user and user != comment.user:
        return False
    now = timezone.now()
    comment_age_seconds = (now - comment.created_at).total_seconds()
    votest_exists = comment.votes_up_count or comment.votes_down_count
    posted_in_editable_window = (
        comment_age_seconds <= get_comment_editable_window_minutes() * 60
    )
    return not votest_exists and posted_in_editable_window
