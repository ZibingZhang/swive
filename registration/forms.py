from django.forms import ModelForm
from registration.models import MeetAthleteRelayEntry, MeetAthleteIndividualEntry
from django.forms.widgets import TextInput


class MeetAthleteIndividualEntryForm(ModelForm):
    class Meta:
        model = MeetAthleteIndividualEntry
        exclude = ("meet", "event")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["seed"].widget = TextInput()


class MeetAthleteRelayEntryForm(ModelForm):
    class Meta:
        model = MeetAthleteRelayEntry
        exclude = ("meet", "event")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["seed"].widget = TextInput()
