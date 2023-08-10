import pytest
from rest_framework_simplejwt.tokens import AccessToken


@pytest.fixture()
def api_client():
    """A Django Rest Framework api test client instance."""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture()
def authed_api_client(api_client):
    def _api_client_authenticator(user):
        api_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user)}"
        )
        return api_client

    return _api_client_authenticator
