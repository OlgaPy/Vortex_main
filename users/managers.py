from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager


class KapibaraUserManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        fields = {self.model.USERNAME_FIELD: username, **extra_fields}
        user = self.model(**fields)
        user.password = make_password(password)
        user.save()
        return user

    def create_superuser(self, external_user_uid, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(
            username=external_user_uid, email=None, password=password, **extra_fields
        )
