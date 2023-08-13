from rest_framework import permissions


class Authenticator(permissions.BasePermission):
    """Class to make sure request comes from authenticator service."""

    def has_permission(self, request, view):
        """Check if actor has permission to manage users."""
        # FIXME: add proper checks
        return True


class OwnUser(permissions.BasePermission):
    """Class to make sure only user can change its own profile."""

    def has_permission(self, request, view):
        """Check if actor is a user itself."""
        user = request.user
        return user.is_authenticated and user.pk == view.get_object().pk
