from django.conf import settings
from django.db.models import QuerySet
from django.utils import timezone

from posts.choices import PostStatus
from posts.models import Post, PostVote
from users.models import UserPublic


def fetch_popular_posts() -> QuerySet[Post]:
    """Fetch posts which have gotten a lot of user activity."""


def fetch_new_posts() -> QuerySet[Post]:
    """Fetch pots which were added recently."""
    return (
        Post.objects.filter(status=PostStatus.PUBLISHED)
        .order_by("-created_at")
        .prefetch_related("tags")
        .select_related("user", "community")
    )


def fetch_draft_posts() -> QuerySet[Post]:
    """Fetch posts in draft status."""
    return (
        Post.objects.filter(status=PostStatus.DRAFT)
        .order_by("-created_at")
        .prefetch_related("tags")
        .select_related("user", "community")
    )


def fetch_user_posts(user: UserPublic) -> QuerySet[Post]:
    """Fetch all user posts, including all statuses."""
    return (
        user.posts.order_by("-created_at")
        .prefetch_related("tags")
        .select_related("user", "community")
    )


def fetch_top_posts() -> QuerySet[Post]:
    """Fetch posts with highest rating."""


def fetch_discussed_posts() -> QuerySet[Post]:
    """Fetch posts with a lot of comments."""


def fetch_bookmarked_posts(user: UserPublic) -> QuerySet[Post]:
    """Fetch posts which user bookmarked."""


def get_post_editable_window_minutes() -> int:
    """Return for how many minutes since posting comment can be edited."""
    return settings.COMMENTS_EDITABLE_WINDOW_MINUTES


def get_post_vote_value_for_author(author: UserPublic, post_vote: PostVote) -> float:
    """Get value of how much rating post author should get on a single post vote."""
    return post_vote.value * settings.POST_RATING_MULTIPLIER


def can_edit_post(user: UserPublic, post: Post) -> bool:
    if user and user != post.user:
        return False
    if post.status != PostStatus.PUBLISHED or not post.published_at:
        return True
    now = timezone.now()
    return (
        now - post.published_at
    ).total_seconds() <= get_post_editable_window_minutes() * 60
