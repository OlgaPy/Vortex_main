from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager


class KapibaraUserManager(UserManager):
    """Custom manager which allow creation of users via ./manage.py command."""

    def _create_user(self, username, email, password, **extra_fields):
        fields = {self.model.USERNAME_FIELD: username, **extra_fields}
        user = self.model(**fields)
        user.password = make_password(password)
        user.save()
        return user
