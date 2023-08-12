import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken


@pytest.fixture()
def api_client():
    """Fixture to be used when need DRF's APIClient."""
    return APIClient()


@pytest.fixture()
def authed_api_client(api_client):
    """Fixture to be used when need to request API as authed user."""

    def api_client_user_auth(user):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user)}")
        return api_client

    return api_client_user_auth


@pytest.fixture()
def anon_api_client(api_client):
    """Fixture to be used when need to request API as anonymous user."""

    def api_client_no_auth():
        return api_client

    return api_client_no_auth
