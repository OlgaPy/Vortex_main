from rest_framework import permissions


class Poster(permissions.BasePermission):
    """Class for managing permissions for users who want to create a post."""

    def has_permission(self, request, view) -> bool:
        """Check if user has permission to post."""
        # TODO: Add checks if user should be allowed to publish posts.
        return True


class PostVoter(permissions.BasePermission):
    """Class for managing permissions for users who want to vote on posts."""

    def has_permission(self, request, view) -> bool:
        """Check if user has permission to vote."""
        # TODO: Add checks if user should be allowed to vote.
        return True
