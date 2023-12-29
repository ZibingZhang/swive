from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group as DjangoGroup
from django.db import models


class Profile(AbstractUser):
    is_coach = models.BooleanField(
        "coach status",
        default=False,
        help_text="Designates whether the user is a coach.",
    )

    class Meta(AbstractUser.Meta):
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def sidebar_display_name(self):
        return self.username if self.name == " " else self.name

    def __str__(self) -> str:
        return f"{self.name} ({self.username})"


class Group(DjangoGroup):
    pass
