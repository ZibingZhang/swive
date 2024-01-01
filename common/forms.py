from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm

from common.models import Athlete, Coach


class BaseForm(Form):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class BaseModelForm(ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class AthleteAdminForm(BaseModelForm):
    class Meta:
        model = Athlete
        exclude = tuple()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self.current_user.is_superuser:
            return
        self.fields["team"].queryset = self.current_user.teams.all()

    def clean(self) -> None:
        if not self.current_user.is_superuser and self.cleaned_data[
            "team"
        ] not in self.current_user.teams.all().values_list("id", flat=True):
            raise ValidationError("Permission denied")


class CoachForm(BaseModelForm):
    COACH_PERMISSIONS = {
        "add_athlete",
        "change_athlete",
        "delete_athlete",
        "view_athlete",
    }

    class Meta:
        model = Coach
        fields = "__all__"

    def save(self, *args, **kwargs) -> Coach:
        # TODO: validate permissions
        profile = self.cleaned_data["profile"]
        profile.is_coach = True
        profile.is_staff = True
        permission_ids = Permission.objects.filter(
            codename__in=CoachForm.COACH_PERMISSIONS
        ).values_list("id", flat=True)
        profile.user_permissions.add(*permission_ids)
        profile.save()
        return super().save(*args, **kwargs)
