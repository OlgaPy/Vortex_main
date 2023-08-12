from django.db.models import QuerySet

from posts.choices import PostStatus
from posts.models import Post
from users.models import UserPublic


def fetch_popular_posts() -> QuerySet[Post]:
    """Fetch posts which have gotten a lot of user activity."""


def fetch_new_posts() -> QuerySet[Post]:
    """Fetch pots which were added recently."""
    return (
        Post.objects.filter(status=PostStatus.PUBLISHED)
        .order_by("-created_at")
        .prefetch_related("tags")
    )


def fetch_draft_posts() -> QuerySet[Post]:
    """Fetch posts in draft status."""
    return (
        Post.objects.filter(status=PostStatus.DRAFT)
        .order_by("-created_at")
        .prefetch_related("tags")
    )


def fetch_user_posts(user: UserPublic) -> QuerySet[Post]:
    """Fetch all user posts, including all statuses."""
    return user.posts.order_by("-created_at").prefetch_related("tags")


def fetch_top_posts() -> QuerySet[Post]:
    """Fetch posts with highest rating."""


def fetch_discussed_posts() -> QuerySet[Post]:
    """Fetch posts with a lot of comments."""


def fetch_bookmarked_posts(user: UserPublic) -> QuerySet[Post]:
    """Fetch posts which user bookmarked."""
