from django.contrib.auth.hashers import make_password, check_password
from django.db import models


class UserPrivate(models.Model):
    name = models.CharField(max_length=25, unique=True, null=False, blank=False)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)

    def set_password(self, password):
        self.password = make_password(password)

    def check_password(self, password):
        return check_password(password, self.password)


class UserPublic(models.Model):
    user = models.OneToOneField(UserPrivate, on_delete=models.CASCADE, primary_key=True)
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
