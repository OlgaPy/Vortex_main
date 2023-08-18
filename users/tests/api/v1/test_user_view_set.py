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

    @pytest.mark.parametrize(
        "action,initial_is_active,post_action_is_active",
        (
            ("activate", False, True),
            ("deactivate", True, False),
        ),
    )
    def test_can_toggle_user_is_active_using_service(
        self, action, initial_is_active, post_action_is_active, anon_api_client, settings
    ):
        settings.INTERNAL_TOKEN_HEADER = self.internal_token_header
        settings.INTERNAL_TOKENS = [self.internal_token]

        user = UserPublicFactory(**self.data, is_active=initial_is_active)

        result = self._activate_deactivate_user(
            action,
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
        assert data["is_active"] is post_action_is_active
        assert user.is_active is post_action_is_active

    @pytest.mark.parametrize(
        "action,initial_is_active", (("activate", False), ("deactivate", True))
    )
    def test_cant_toggle_user_is_active_with_wrong_header_name(
        self, action, initial_is_active, anon_api_client, settings
    ):
        settings.INTERNAL_TOKENS = [self.internal_token]
        user = UserPublicFactory(**self.data, is_active=initial_is_active)
        result = self._activate_deactivate_user(
            action,
            anon_api_client(),
            user,
            headers={"X-Wrong-Header": self.internal_token},
        )
        user.refresh_from_db()
        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert user.is_active is initial_is_active

    @pytest.mark.parametrize(
        "action,initial_is_active", (("activate", False), ("deactivate", True))
    )
    def test_cant_toggle_is_active_with_wrong_token(
        self, action, initial_is_active, anon_api_client, settings
    ):
        settings.INTERNAL_TOKEN_HEADER = self.internal_token_header
        user = UserPublicFactory(**self.data, is_active=initial_is_active)
        result = self._activate_deactivate_user(
            action,
            anon_api_client(),
            user,
            headers={self.internal_token_header: "wrong_value"},
        )
        user.refresh_from_db()
        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert user.is_active is initial_is_active

    @pytest.mark.parametrize(
        "action,initial_is_active", (("activate", False), ("deactivate", True))
    )
    def test_cant_toggle_is_active_without_headers(
        self, action, initial_is_active, anon_api_client
    ):
        user = UserPublicFactory(**self.data, is_active=initial_is_active)
        result = self._activate_deactivate_user(action, anon_api_client(), user)
        user.refresh_from_db()
        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert user.is_active is initial_is_active

    @pytest.mark.parametrize("is_superuser", (True, False))
    @pytest.mark.parametrize("is_staff", (True, False))
    @pytest.mark.parametrize(
        "action,initial_is_active", (("activate", False), ("deactivate", True))
    )
    def test_cant_activate_as_logged_in_user(
        self, action, initial_is_active, is_staff, is_superuser, authed_api_client
    ):
        user = UserPublicFactory(
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=initial_is_active,
        )
        result = self._activate_deactivate_user(action, authed_api_client(user), user)
        user.refresh_from_db()
        assert result.status_code == (
            status.HTTP_403_FORBIDDEN
            if initial_is_active
            else status.HTTP_401_UNAUTHORIZED
        )
        assert user.is_active is initial_is_active

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

    def test_can_update_own_account(self, authed_api_client):
        new_dob = "2020-01-01"
        new_bio = "new kapibio"
        user = UserPublicFactory()

        result = self._update_user(
            authed_api_client(user),
            user,
            data={
                "date_of_birth": new_dob,
                "bio": new_bio,
            },
        )
        user.refresh_from_db()

        data = result.data
        assert result.status_code == status.HTTP_200_OK
        assert data["date_of_birth"] == new_dob
        assert data["bio"] == new_bio
        assert f"{user.date_of_birth:%Y-%m-%d}" == new_dob
        assert user.bio == new_bio

    def test_cant_update_readonly_fields(self, authed_api_client):
        initial_rating = 1
        initial_comments_count = 1
        initial_votes_up_count = 1
        initial_votes_down_count = 1
        user = UserPublicFactory()

        result = self._update_user(
            authed_api_client(user),
            user,
            data={
                "rating": 1000,
                "comments_count": 100,
                "votes_up_count": 200,
                "votes_down_count": 300,
            },
        )
        user.refresh_from_db()

        data = result.data
        assert result.status_code == status.HTTP_200_OK
        assert data["rating"] == initial_rating
        assert data["comments_count"] == initial_comments_count
        assert data["votes_up_count"] == initial_votes_up_count
        assert data["votes_down_count"] == initial_votes_down_count
        assert user.rating == initial_rating
        assert user.comments_count == initial_comments_count
        assert user.votes_up_count == initial_votes_up_count
        assert user.votes_down_count == initial_votes_down_count

    def test_cant_update_other_account(self, authed_api_client):
        initial_date_of_birth = "2000-01-01"
        initial_bio = "viva la kapibara"
        other_user = UserPublicFactory(
            date_of_birth=initial_date_of_birth,
            bio=initial_bio,
        )
        user = UserPublicFactory()
        result = self._update_user(
            authed_api_client(user),
            other_user,
            data={
                "date_of_birth": "2020-01-01",
                "bio": "new kapibio",
            },
        )
        other_user.refresh_from_db()

        data = result.data
        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert data["date_of_birth"] == initial_date_of_birth
        assert data["bio"] == initial_bio
        assert f"{user.date_of_birth:%Y-%m-%d}" == initial_date_of_birth
        assert user.bio == initial_bio

    def _create_user(self, client, data, headers=None):
        return client.post(reverse("v1:users:users-list"), data=data, headers=headers)

    def _activate_deactivate_user(self, action, client, user, headers=None):
        return client.post(
            reverse(
                f"v1:users:users-{action}",
                kwargs={"external_user_uid": user.external_user_uid},
            ),
            headers=headers,
        )

    def _update_user(self, client, user, data):
        return client.patch(
            reverse(
                "v1:users:users-detail",
                kwargs={"external_user_uid": user.external_user_uid},
            ),
            data=data,
        )
