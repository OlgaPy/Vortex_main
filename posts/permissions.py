from rest_framework import permissions


class Poster(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        # TODO: Add checks if user should be allowed to publish posts.
        return True


class PostVoter(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        # TODO: Add checks if user should be allowed to vote.
        return True
