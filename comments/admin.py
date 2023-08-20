from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from comments.models import Comment


@admin.register(Comment)
class CommentAdmin(MPTTModelAdmin):
    mptt_indent_field = "short_content"
    list_display_links = ("short_content",)
    list_display = (
        "short_content",
        "username",
        "post_title",
        "votes_up_count",
        "votes_down_count",
        "rating",
    )
    fields = (
        "post",
        "parent",
        "user",
        "content",
        "votes_up_count",
        "votes_down_count",
        "rating",
        # "created_at",
    )
    raw_id_fields = (
        "post",
        "user",
        "parent",
    )
    readonly_fields = (
        "votes_up_count",
        "votes_down_count",
        "rating",
    )
    list_select_related = (
        "user",
        "post",
        "parent",
    )
    search_fields = (
        "user__username",
        "user__email",
        "post__title",
        "content",
    )

    def short_content(self, obj: Comment) -> str:
        """Get short version of published content."""
        return obj.content[:100]

    def username(self, obj: Comment) -> str:
        """Get author's username."""
        return obj.user.username

    def post_title(self, obj: Comment) -> str:
        """Get title of the post."""
        return obj.post.title
