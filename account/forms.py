from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from account.models import Profile


class ProfileCreationForm(UserCreationForm):
    class Meta:
        model = Profile
        fields = ("first_name", "last_name", "email", "username")


class ProfileChangeForm(UserChangeForm):
    class Meta:
        model = Profile
        fields = ("first_name", "last_name", "email", "username", "password")
