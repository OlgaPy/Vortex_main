from django.db.models import QuerySet

from posts.choices import PostStatus
from posts.models import Post
from users.models import UserPublic


def fetch_popular_posts() -> QuerySet[Post]:
    """Публикации, которые в данный момент активно комментируются, лайкаются и
    просматриваются. Этот раздел предназначен для того, чтобы пользователь мог
    видеть самый актуальный и популярный контент."""


def fetch_new_posts() -> QuerySet[Post]:
    """Недавно добавленные публикации без учета их популярности или активности."""
    return (
        Post.objects.filter(status=PostStatus.PUBLISHED)
        .order_by("-created_at")
        .prefetch_related("tags")
    )


def fetch_draft_posts() -> QuerySet[Post]:
    """Посты-черновики, в основном нужны для вывода для автора."""
    return (
        Post.objects.filter(status=PostStatus.DRAFT)
        .order_by("-created_at")
        .prefetch_related("tags")
    )


def fetch_user_posts(user: UserPublic) -> QuerySet[Post]:
    """Все посты автора."""
    return user.posts.order_by("-created_at").prefetch_related("tags")


def fetch_top_posts() -> QuerySet[Post]:
    """Публикации с самым высоким рейтингом за определенный промежуток времени
    (день, неделя, месяц, все время)."""


def fetch_discussed_posts() -> QuerySet[Post]:
    ...


def fetch_bookmarked_posts(user: UserPublic) -> QuerySet[Post]:
    ...
