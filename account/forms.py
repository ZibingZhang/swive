from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from account.models import Profile


class ProfileCreationForm(UserCreationForm):
    class Meta:
        model = Profile
        fields = ("first_name", "last_name", "email", "username")


class ProfileChangeForm(UserChangeForm):
    class Meta:
        model = Profile
        fields = ("first_name", "last_name", "email", "username")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        del self.fields["password"]


class AdminProfileChangeForm(UserChangeForm):
    class Meta:
        model = Profile
        fields = ("first_name",)
        exclude = tuple()
