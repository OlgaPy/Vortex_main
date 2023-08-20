from rest_framework import permissions


class CommentPoster(permissions.BasePermission):
    """Class for managing permissions for users who wants to post a comment."""

    def has_permission(self, request, view) -> bool:
        """Check if user has permission to comment."""
        # TODO: Add checks if user should be allowed to post comment.
        return True
