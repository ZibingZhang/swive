from collections import defaultdict
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from registration.models import Athlete
from common.constants import INDIVIDUAL_EVENTS, EVENT_ORDER
from registration.forms import MeetAthleteRelayEntryForm, MeetAthleteIndividualEntryForm, AthleteForm
from registration.models import MeetAthleteIndividualEntry


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@login_required
def meet_entry_form(request, meet_id, team_id):
    if request.method == "GET":
        sections = []
        entries = MeetAthleteIndividualEntry.objects.filter(meet_id=meet_id, athlete__team_id=team_id)
        entries_by_event = defaultdict(lambda: [])
        for entry in entries:
            entries_by_event[entry.event].append(entry)
        for event in EVENT_ORDER:
            if event in INDIVIDUAL_EVENTS:
                forms = []
                for i in range(4):
                    try:
                        forms.append(MeetAthleteIndividualEntryForm(team_id, prefix=f"{event.as_prefix()}-{i}", initial={"athlete": entries_by_event[event][i].athlete_id, "seed": entries_by_event[event][i].seed}))
                    except IndexError:
                        forms.append(MeetAthleteIndividualEntryForm(team_id, prefix=f"{event.as_prefix()}-{i}"))
                sections.append({
                    "event": event.value,
                    "forms": forms
                })
        return render(request, "meet_entry.html", {"sections": sections})


@login_required
def save_meet_entry_form(request, meet_id, team_id):
    if request.method == "POST":
        print(request._post)
        return HttpResponse(200)


@login_required
def athlete(request):
    if request.method == "GET":
        return render(request, "athletes.html", {"form": AthleteForm(), "athletes": Athlete.objects.filter()})
