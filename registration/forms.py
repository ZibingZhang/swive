from __future__ import annotations

from django import forms

from common.forms import BaseForm, BaseModelForm
from common.utils import is_seed
from registration.models import Athlete


class AthleteForm(BaseModelForm):
    class Meta:
        model = Athlete
        fields = "__all__"


class MeetEntryForm(BaseForm):
    seed = forms.CharField(max_length=10, required=False)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def athlete_fields(self):
        return (field for field in self.visible_fields() if "athlete" in field.name)

    @property
    def seed_field(self):
        return next(field for field in self.visible_fields() if "seed" == field.name)

    def clean(self) -> None:
        if not is_seed(self.cleaned_data["seed"]):
            self.add_error("seed", "Seed not formatted properly")


class MeetIndividualEntryForm(MeetEntryForm):
    athlete = forms.TypedChoiceField(
        choices=[("", "")], required=False, coerce=int, empty_value=None
    )

    def __init__(self, athlete_choices: list[Athlete], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["athlete"].choices += [
            (athlete.id, str(athlete)) for athlete in athlete_choices
        ]

    def clean(self) -> None:
        super().clean()


class MeetRelayEntryForm(MeetEntryForm):
    athlete_1 = forms.TypedChoiceField(
        choices=[("", "")], required=False, coerce=int, empty_value=None
    )
    athlete_2 = forms.TypedChoiceField(
        choices=[("", "")], required=False, coerce=int, empty_value=None
    )
    athlete_3 = forms.TypedChoiceField(
        choices=[("", "")], required=False, coerce=int, empty_value=None
    )
    athlete_4 = forms.TypedChoiceField(
        choices=[("", "")], required=False, coerce=int, empty_value=None
    )

    def __init__(self, athlete_choices: list[Athlete], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["athlete_1"].choices += [
            (athlete.id, str(athlete)) for athlete in athlete_choices
        ]
        self.fields["athlete_2"].choices += [
            (athlete.id, str(athlete)) for athlete in athlete_choices
        ]
        self.fields["athlete_3"].choices += [
            (athlete.id, str(athlete)) for athlete in athlete_choices
        ]
        self.fields["athlete_4"].choices += [
            (athlete.id, str(athlete)) for athlete in athlete_choices
        ]

    def clean(self) -> None:
        super().clean()
