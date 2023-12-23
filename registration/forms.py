from __future__ import annotations

from django.forms.widgets import TextInput

from common.forms import BaseModelForm
from registration.models import (
    Athlete,
    MeetAthleteIndividualEntry,
    MeetAthleteRelayEntry,
)


class AthleteForm(BaseModelForm):
    class Meta:
        model = Athlete
        fields = "__all__"


class MeetEntryForm(BaseModelForm):
    def __init__(self, team_pk, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if "athlete" in name:
                field.required = False
                field.empty_label = ""
                self._filter_athlete_choices(field, team_pk)
        self.fields["seed"].widget = TextInput()

    @property
    def athlete_fields(self):
        return (field for field in self.visible_fields() if "athlete" in field.name)

    @property
    def seed_field(self):
        return next(field for field in self.visible_fields() if "seed" == field.name)

    @staticmethod
    def _filter_athlete_choices(field, team_pk: int):
        field.choices = filter(
            lambda choice: choice[0] == "" or choice[0].instance.team.pk == team_pk,
            field.choices,
        )


class MeetAthleteIndividualEntryForm(MeetEntryForm):
    class Meta:
        model = MeetAthleteIndividualEntry
        exclude = ("meet", "event")

    def __init__(self, team_pk, *args, **kwargs) -> None:
        super().__init__(team_pk, *args, **kwargs)


class MeetAthleteRelayEntryForm(MeetEntryForm):
    class Meta:
        model = MeetAthleteRelayEntry
        exclude = ("meet", "event")

    def __init__(self, team_pk, *args, **kwargs) -> None:
        super().__init__(team_pk, *args, **kwargs)
