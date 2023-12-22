from django.contrib.auth.models import AbstractUser


class Profile(AbstractUser):
    class Meta(AbstractUser.Meta):
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
