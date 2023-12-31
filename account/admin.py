from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin
from django.contrib.auth.admin import Group as DjangoGroup
from django.contrib.auth.admin import GroupAdmin, UserAdmin

from account.models import Group, Profile
from common.admin import BaseAdmin

if TYPE_CHECKING:
    from django.http import HttpRequest

admin.site.unregister(DjangoGroup)


@admin.register(Profile)
class ProfileAdmin(UserAdmin, BaseAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_official",
                    "is_coach",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    list_display = ("username", "email", "first_name", "last_name", "is_staff")

    def get_queryset(self, request: HttpRequest):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(pk=request.user.pk)


@admin.register(Group)
class GroupAdmin(GroupAdmin, BaseAdmin):
    pass
