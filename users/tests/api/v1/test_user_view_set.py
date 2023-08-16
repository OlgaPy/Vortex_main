import uuid

import faker
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from users.tests.factories import UserPublicFactory


@pytest.mark.django_db
class TestUsersViewSet:
    def setup(self):
        self.internal_token_header = "X-Test-Header"
        self.internal_token = "test-token"
        self.username = "any-username"
        self.email = "test@kapi.bar"
        self.external_user_uid = str(uuid.uuid4())
        self.data = {
            "external_user_uid": self.external_user_uid,
            "username": self.username,
            "email": self.email,
        }

    def test_can_create_inactive_user_using_service(self, anon_api_client, settings):
        settings.INTERNAL_TOKEN_HEADER = self.internal_token_header
        settings.INTERNAL_TOKENS = [self.internal_token]

        result = self._create_user(
            anon_api_client(),
            self.data,
            headers={self.internal_token_header: self.internal_token},
        )
        assert result.status_code == status.HTTP_201_CREATED
        data = result.data
        assert data["external_user_uid"] == self.external_user_uid
        assert data["username"] == self.username
        assert data["email"] == self.email
        assert data["is_active"] is False

    def test_can_activate_inactive_user_using_service(self, anon_api_client, settings):
        settings.INTERNAL_TOKEN_HEADER = self.internal_token_header
        settings.INTERNAL_TOKENS = [self.internal_token]

        user = UserPublicFactory(**self.data, is_active=False)

        result = self._activate_user(
            anon_api_client(),
            user,
            headers={self.internal_token_header: self.internal_token},
        )
        user.refresh_from_db()
        assert result.status_code == status.HTTP_200_OK
        data = result.data
        assert data["external_user_uid"] == self.external_user_uid
        assert data["username"] == self.username
        assert data["email"] == self.email
        assert data["is_active"] is True
        assert user.is_active is True

    def test_cant_activate_with_wrong_header_name(self, anon_api_client, settings):
        settings.INTERNAL_TOKENS = [self.internal_token]
        user = UserPublicFactory(**self.data, is_active=False)
        result = self._activate_user(
            anon_api_client(),
            user,
            headers={"X-Wrong-Header": self.internal_token},
        )
        user.refresh_from_db()
        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert user.is_active is False

    def test_cant_activate_with_wrong_token(self, anon_api_client, settings):
        settings.INTERNAL_TOKEN_HEADER = self.internal_token_header
        user = UserPublicFactory(**self.data, is_active=False)
        result = self._activate_user(
            anon_api_client(),
            user,
            headers={self.internal_token_header: "wrong_value"},
        )
        user.refresh_from_db()
        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert user.is_active is False

    def test_cant_activate_without_headers(self, anon_api_client):
        user = UserPublicFactory(**self.data, is_active=False)
        result = self._activate_user(anon_api_client(), user)
        user.refresh_from_db()
        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert user.is_active is False

    @pytest.mark.parametrize("is_superuser", (True, False))
    @pytest.mark.parametrize("is_staff", (True, False))
    def test_cant_activate_as_logged_in_user(
        self, is_staff, is_superuser, authed_api_client
    ):
        user = UserPublicFactory(
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        result = self._activate_user(authed_api_client(user), user)
        assert result.status_code == status.HTTP_403_FORBIDDEN

    def test_cant_create_with_wrong_header_name(self, anon_api_client, settings):
        settings.INTERNAL_TOKENS = [self.internal_token]
        result = self._create_user(
            anon_api_client(),
            self.data,
            headers={"X-Wrong-Header": self.internal_token},
        )
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cant_create_with_wrong_token(self, anon_api_client, settings):
        settings.INTERNAL_TOKEN_HEADER = self.internal_token_header
        result = self._create_user(
            anon_api_client(),
            self.data,
            headers={self.internal_token_header: "wrong_value"},
        )
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cant_create_without_headers(self, anon_api_client):
        result = self._create_user(anon_api_client(), self.data)
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize("is_superuser", (True, False))
    @pytest.mark.parametrize("is_staff", (True, False))
    def test_cant_create_as_logged_in_user(
        self, is_staff, is_superuser, authed_api_client
    ):
        user = UserPublicFactory(
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        result = self._create_user(authed_api_client(user), self.data)
        assert result.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize("is_active", (True, False))
    @pytest.mark.parametrize("field_name", ("external_user_uid", "username", "email"))
    def test_cant_create_user_with_same_fields(
        self, field_name, is_active, anon_api_client, settings
    ):
        settings.INTERNAL_TOKEN_HEADER = self.internal_token_header
        settings.INTERNAL_TOKENS = [self.internal_token]

        # Existing user
        UserPublicFactory(**self.data, is_active=is_active)

        # Creating fake data for a new user
        fake = faker.Faker()
        data = {
            "external_user_uid": str(uuid.uuid4()),
            "username": fake.user_name(),
            "email": fake.email(),
        }

        result = self._create_user(
            anon_api_client(),
            {
                **data,
                # replace field with data present on existing user
                field_name: self.data[field_name],
            },
            headers={self.internal_token_header: self.internal_token},
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

    def _create_user(self, client, data, headers=None):
        return client.post(reverse("v1:users:users-list"), data=data, headers=headers)

    def _activate_user(self, client, user, headers=None):
        return client.post(
            reverse(
                "v1:users:users-activate",
                kwargs={"external_user_uid": user.external_user_uid},
            ),
            headers=headers,
        )
