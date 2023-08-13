import pytest


@pytest.mark.django_db
class TestUsersViewSet:
    def test_can_update_only_own_user_profile(self):
        raise AssertionError
