from django.forms import Form, ModelForm

from common.models import Athlete, Team
from registration.models import CoachEntry


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
        team_pks = CoachEntry.objects.filter(profile=self.current_user).values_list(
            "team_id", flat=True
        )
        self.fields["team"].queryset = Team.objects.filter(id__in=team_pks)
