from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import UserPublic


@admin.register(UserPublic)
class UserPublicAdmin(admin.ModelAdmin):
    ordering = ("external_user_uid",)
    list_display = (
        "external_user_uid",
        "is_staff",
        "is_superuser",
    )
