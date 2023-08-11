import pytest
from rest_framework_simplejwt.tokens import AccessToken


@pytest.fixture()
def api_client():
    """A Django Rest Framework api test client instance."""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture()
def authed_api_client(api_client):
    def api_client_user_auth(user):
        api_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user)}"
        )
        return api_client

    return api_client_user_auth


@pytest.fixture()
def anon_api_client(api_client):
    def api_client_no_auth():
        return api_client

    return api_client_no_auth
