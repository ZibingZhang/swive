from __future__ import annotations

from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm

from common.models import Athlete


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
