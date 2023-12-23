from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group as DjangoGroup


class Profile(AbstractUser):
    class Meta(AbstractUser.Meta):
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.username})"


class Group(DjangoGroup):
    pass
