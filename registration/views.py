from collections import defaultdict
from decimal import Decimal

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from registration.models import Athlete, Meet
from common.constants import INDIVIDUAL_EVENTS, EVENT_ORDER, RELAY_EVENTS
from django.views.decorators.http import require_http_methods
from registration.forms import MeetAthleteRelayEntryForm, MeetAthleteIndividualEntryForm, AthleteForm
from registration.models import MeetAthleteIndividualEntry, MeetAthleteRelayEntry


@login_required
@require_http_methods(["GET"])
def manage_athletes(request):
    return render(request, "athletes.html", {"form": AthleteForm(), "athletes": Athlete.objects.filter()})


@login_required
@require_http_methods(["GET"])
def meet_entry_form(request, meet_id, team_id):
    sections = []
    individual_entries = MeetAthleteIndividualEntry.objects.filter(meet_id=meet_id, athlete__team_id=team_id)
    relay_entries = MeetAthleteRelayEntry.objects.filter(meet_id=meet_id, athlete_1__team_id=team_id)
    entries_by_event = defaultdict(lambda: [])

    for entry in individual_entries:
        entries_by_event[entry.event].append(entry)
    for entry in relay_entries:
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
        elif event in RELAY_EVENTS:
            forms = []
            for i in range(4):
                try:
                    forms.append(MeetAthleteRelayEntryForm(team_id, prefix=f"{event.as_prefix()}-{i}", initial={
                        "athlete_1": entries_by_event[event][i].athlete_1_id, "seed": entries_by_event[event][i].seed}))
                except IndexError:
                    forms.append(MeetAthleteRelayEntryForm(team_id, prefix=f"{event.as_prefix()}-{i}"))
            sections.append({
                "event": event.value,
                "forms": forms
            })

    return render(request, "meet_entry.html", {"sections": sections})


@login_required
@require_http_methods(["POST"])
def save_meet_entry_form(request, meet_id, team_id):
    entries = MeetAthleteIndividualEntry.objects.filter(meet_id=meet_id, athlete__team_id=team_id)
    entries_by_event_athlete_id = {}
    for entry in entries:
        entries_by_event_athlete_id[(entry.event, str(entry.athlete.id))] = entry
    for event in INDIVIDUAL_EVENTS:
        for i in range(4):
            athlete_id = request.POST[f"{event.as_prefix()}-{i}-athlete"]
            seed = request.POST[f"{event.as_prefix()}-{i}-seed"]
            if athlete_id == "" or seed == "":
                # TODO: validation error
                continue
            entry = entries_by_event_athlete_id.get((event, athlete_id))
            if entry:
                entry.seed = Decimal(seed)
                entry.save()
                del entries_by_event_athlete_id[(event, athlete_id)]
            else:
                if seed:
                    MeetAthleteIndividualEntry.objects.create(meet_id=meet_id, athlete_id=int(athlete_id), event=event, seed=Decimal(seed))
                else:
                    MeetAthleteIndividualEntry.objects.create(meet_id=meet_id, athlete_id=int(athlete_id), event=event)

    for entry in entries_by_event_athlete_id.values():
        entry.delete()
    return HttpResponse()
