from django.contrib import admin

from users.models import UserPublic


@admin.register(UserPublic)
class UserPublicAdmin(admin.ModelAdmin):
    ordering = ("external_user_uid",)
    list_display = (
        "__str__",
        "is_staff",
        "is_superuser",
    )
