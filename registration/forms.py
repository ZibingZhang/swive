from __future__ import annotations

from django import forms

from common.forms import BaseForm, BaseModelForm
from common.utils import is_seed
from registration.models import CoachEntry

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from registration.models import Athlete


class CoachEntryForm(BaseModelForm):
    class Meta:
        model = CoachEntry
        fields = "__all__"

    def save(self, *args, **kwargs) -> CoachEntry:
        profile = self.cleaned_data["profile"]
        profile.is_coach = True
        profile.save()
        return super().save(*args, **kwargs)


class MeetEntryForm(BaseForm):
    order = forms.IntegerField(min_value=0, widget=forms.HiddenInput())
    seed = forms.CharField(max_length=10, required=False, empty_value=None)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def athlete_fields(self):
        return (field for field in self.visible_fields() if "athlete" in field.name)

    @property
    def seed_field(self):
        return next(field for field in self.visible_fields() if "seed" == field.name)

    def clean(self) -> None:
        if self.cleaned_data["seed"] is None:
            return
        for field in self.athlete_fields:
            if self.cleaned_data[field.name] is None:
                self.add_error(field.name, "Missing athlete")
        if not is_seed(self.cleaned_data["seed"]):
            self.add_error("seed", "Seed not formatted properly")


class MeetIndividualEntryForm(MeetEntryForm):
    athlete = forms.TypedChoiceField(
        choices=[("", "")], required=False, coerce=int, empty_value=None
    )

    def __init__(self, athlete_choices: list[Athlete], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["athlete"].choices += [
            (athlete.pk, athlete) for athlete in athlete_choices
        ]


class MeetRelayEntryForm(MeetEntryForm):
    athlete_0 = forms.TypedChoiceField(
        choices=[("", "")], required=False, coerce=int, empty_value=None
    )
    athlete_1 = forms.TypedChoiceField(
        choices=[("", "")], required=False, coerce=int, empty_value=None
    )
    athlete_2 = forms.TypedChoiceField(
        choices=[("", "")], required=False, coerce=int, empty_value=None
    )
    athlete_3 = forms.TypedChoiceField(
        choices=[("", "")], required=False, coerce=int, empty_value=None
    )

    def __init__(self, athlete_choices: list[Athlete], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["athlete_0"].choices += [
            (athlete.pk, athlete) for athlete in athlete_choices
        ]
        self.fields["athlete_1"].choices += [
            (athlete.pk, athlete) for athlete in athlete_choices
        ]
        self.fields["athlete_2"].choices += [
            (athlete.pk, athlete) for athlete in athlete_choices
        ]
        self.fields["athlete_3"].choices += [
            (athlete.pk, athlete) for athlete in athlete_choices
        ]
