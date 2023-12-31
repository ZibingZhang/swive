from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.contrib.auth.models import Permission

from common import utils
from common.forms import BaseForm, BaseModelForm
from registration.models import CoachEntry

if TYPE_CHECKING:
    from registration.models import Athlete


class CoachEntryForm(BaseModelForm):
    COACH_PERMISSIONS = {
        "add_athlete",
        "change_athlete",
        "delete_athlete",
        "view_athlete",
    }

    class Meta:
        model = CoachEntry
        fields = "__all__"

    def save(self, *args, **kwargs) -> CoachEntry:
        # TODO: validate permissions
        profile = self.cleaned_data["profile"]
        profile.is_coach = True
        profile.is_staff = True
        permission_ids = Permission.objects.filter(
            codename__in=CoachEntryForm.COACH_PERMISSIONS
        ).values_list("id", flat=True)
        profile.user_permissions.add(*permission_ids)
        profile.save()
        return super().save(*args, **kwargs)


class MeetEntryForm(BaseForm):
    order = forms.IntegerField(min_value=0, widget=forms.HiddenInput())
    seed = forms.CharField(max_length=10, required=False, empty_value=None)

    def __init__(self, *args, **kwargs) -> None:
        initial = kwargs.get("initial")
        if initial and initial.get("seed"):
            initial["seed"] = utils.format_seed(initial["seed"])
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
        if not utils.is_seed(self.cleaned_data["seed"]):
            self.add_error("seed", "Seed not formatted properly")
        self.cleaned_data["seed"] = utils.seed_to_decimal(self.cleaned_data["seed"])


class MeetIndividualEntryForm(MeetEntryForm):
    athlete = forms.TypedChoiceField(
        choices=[("", "")], required=False, coerce=int, empty_value=None
    )

    def __init__(self, athlete_choices: list[Athlete], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["athlete"].choices += [
            (athlete.id, athlete) for athlete in athlete_choices
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
            (athlete.id, athlete) for athlete in athlete_choices
        ]
        self.fields["athlete_1"].choices += [
            (athlete.id, athlete) for athlete in athlete_choices
        ]
        self.fields["athlete_2"].choices += [
            (athlete.id, athlete) for athlete in athlete_choices
        ]
        self.fields["athlete_3"].choices += [
            (athlete.id, athlete) for athlete in athlete_choices
        ]
