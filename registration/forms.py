from django.forms import ModelForm, ChoiceField
from registration.models import MeetAthleteRelayEntry, MeetAthleteIndividualEntry, Athlete
from django.forms.widgets import TextInput


class AthleteForm(ModelForm):
    class Meta:
        model = Athlete
        fields = "__all__"


class MeetAthleteIndividualEntryForm(ModelForm):
    class Meta:
        model = MeetAthleteIndividualEntry
        exclude = ("meet", "event")

    def __init__(self, team_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["athlete"].required = False
        self.fields["seed"].widget = TextInput()

        self._filter_athlete_choices(self.fields["athlete"], team_id)

    @staticmethod
    def _filter_athlete_choices(field, team_id):
        field.choices = filter(
            lambda choice: choice[0] == "" or choice[0].instance.team_id == team_id,
            field.choices
        )


class MeetAthleteRelayEntryForm(ModelForm):
    class Meta:
        model = MeetAthleteRelayEntry
        exclude = ("meet", "event")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["seed"].widget = TextInput()
