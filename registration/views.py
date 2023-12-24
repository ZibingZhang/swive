from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from common.constants import EVENT_ORDER, INDIVIDUAL_EVENTS, RELAY_EVENTS
from common.models import Meet, Team
from registration.forms import (
    AthleteForm,
    MeetAthleteIndividualEntryForm,
    MeetAthleteRelayEntryForm,
)
from registration.models import (
    Athlete,
    CoachEntry,
    MeetAthleteIndividualEntry,
    MeetAthleteRelayEntry,
    MeetTeamEntry,
)

if TYPE_CHECKING:
    from django.http import HttpRequest

    from account.models import Profile


@login_required
@require_http_methods(["GET"])
def manage_athletes(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "athletes.html",
        {"form": AthleteForm(), "athletes": Athlete.objects.filter()},
    )


@login_required
@require_http_methods(["GET"])
def meet_entry_form(request: HttpRequest, meet_pk, team_pk) -> HttpResponse:
    _validate_request(request.user, meet_pk, team_pk)

    sections = []
    individual_entries = MeetAthleteIndividualEntry.objects.filter(
        meet__pk=meet_pk, athlete__team__pk=team_pk
    )
    relay_entries = MeetAthleteRelayEntry.objects.filter(
        meet__pk=meet_pk, athlete_1__team__pk=team_pk
    )
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
                    forms.append(
                        MeetAthleteIndividualEntryForm(
                            team_pk,
                            prefix=f"{event.as_prefix()}-{i}",
                            initial={
                                "athlete": entries_by_event[event][i].athlete.pk,
                                "seed": entries_by_event[event][i].seed,
                            },
                        )
                    )
                except IndexError:
                    forms.append(
                        MeetAthleteIndividualEntryForm(
                            team_pk, prefix=f"{event.as_prefix()}-{i}"
                        )
                    )
            sections.append({"event": event.value, "forms": forms})
        elif event in RELAY_EVENTS:
            forms = []
            for i in range(4):
                try:
                    forms.append(
                        MeetAthleteRelayEntryForm(
                            team_pk,
                            prefix=f"{event.as_prefix()}-{i}",
                            initial={
                                "athlete_1": entries_by_event[event][i].athlete_1.pk,
                                "seed": entries_by_event[event][i].seed,
                            },
                        )
                    )
                except IndexError:
                    forms.append(
                        MeetAthleteRelayEntryForm(
                            team_pk, prefix=f"{event.as_prefix()}-{i}"
                        )
                    )
            sections.append({"event": event.value, "forms": forms})

    return render(request, "meet_entry.html", {"sections": sections})


@login_required
@require_http_methods(["POST"])
def save_meet_entry_form(
    request: HttpRequest, meet_pk: int, team_pk: int
) -> HttpResponse:
    _validate_request(request.user, meet_pk, team_pk)

    entries = MeetAthleteIndividualEntry.objects.filter(
        meet__pk=meet_pk, athlete__team__pk=team_pk
    )
    entries_by_event_athlete_pk = {}
    for entry in entries:
        entries_by_event_athlete_pk[(entry.event, str(entry.athlete.pk))] = entry
    for event in INDIVIDUAL_EVENTS:
        for i in range(4):
            athlete_pk = request.POST[f"{event.as_prefix()}-{i}-athlete"]
            seed = request.POST[f"{event.as_prefix()}-{i}-seed"]
            if athlete_pk == "" or seed == "":
                # TODO: validation error
                continue
            entry = entries_by_event_athlete_pk.get((event, athlete_pk))
            if entry:
                entry.seed = Decimal(seed)
                entry.save()
                del entries_by_event_athlete_pk[(event, athlete_pk)]
            else:
                if seed:
                    MeetAthleteIndividualEntry.objects.create(
                        meet__pk=meet_pk,
                        athlete_pk=int(athlete_pk),
                        event=event,
                        seed=Decimal(seed),
                    )
                else:
                    MeetAthleteIndividualEntry.objects.create(
                        meet__pk=meet_pk, athlete_pk=int(athlete_pk), event=event
                    )

    for entry in entries_by_event_athlete_pk.values():
        entry.delete()
    return HttpResponse()


def _validate_request(user: Profile, meet_pk: int, team_pk: int) -> None:
    if not Meet.objects.filter(pk=meet_pk).exists():
        raise Http404("Meet not found")
    if not Team.objects.filter(pk=team_pk).exists():
        raise Http404("Team not found")
    if not MeetTeamEntry.objects.filter(meet__pk=meet_pk, team__pk=team_pk).exists():
        raise Http404("Team not registered to meet")

    if user.is_superuser:
        return
    team_pks = CoachEntry.objects.filter(profile=user).values_list(
        "team__pk", flat=True
    )
    if team_pk not in team_pks:
        raise PermissionDenied("User is not registered to the team")
