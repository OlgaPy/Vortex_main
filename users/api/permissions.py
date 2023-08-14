from rest_framework import permissions

from common.helpers import is_request_signed_with_valid_internal_token


class Authenticator(permissions.BasePermission):
    """Class to make sure request comes from authenticator service."""

    def has_permission(self, request, view):
        """Check if actor has permission to manage users."""
        return is_request_signed_with_valid_internal_token(request)


class LoadtestWorker(permissions.BasePermission):
    """Class to make sure request omes from loadtest suite."""

    def has_permission(self, request, view):
        """Check if actor has permission to perform loadtesting."""
        return is_request_signed_with_valid_internal_token(request)


class OwnUser(permissions.BasePermission):
    """Class to make sure only user can change its own profile."""

    def has_permission(self, request, view):
        """Check if actor is a user itself."""
        user = request.user
        return user.is_authenticated and user.pk == view.get_object().pk
