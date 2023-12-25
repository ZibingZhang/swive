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
from registration.constants import ENTRIES_PER_EVENT
from registration.forms import (
    AthleteForm,
    MeetAthleteIndividualEntryForm,
    MeetAthleteRelayEntryForm,
)
from registration.models import (
    Athlete,
    CoachEntry,
    MeetIndividualEntry,
    MeetRelayEntry,
    MeetTeamEntry,
)

if TYPE_CHECKING:
    from django.http import HttpRequest

    from account.models import Profile
    from common.constants import Event
    from common.forms import BaseModelForm
    from registration.models import MeetEntry

from typing import TypedDict


class Section(TypedDict):
    event: Event
    count: int
    forms: list[BaseModelForm]


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
def meet_entries_for_team(
    request: HttpRequest, meet_pk: int, team_pk: int
) -> HttpResponse:
    _validate_request(request.user, meet_pk, team_pk)

    sections = []
    entries_by_event = _build_entries_by_event(meet_pk, team_pk)
    for event in EVENT_ORDER:
        sections.append(_create_event_section(team_pk, entries_by_event, event))
    return render(request, "meet-entry.html", {"sections": sections})


def _build_entries_by_event(meet_pk: int, team_pk: int) -> dict[Event, list[MeetEntry]]:
    entries_by_event = defaultdict(lambda: [])
    for individual_entry in MeetIndividualEntry.objects.filter(
        meet__pk=meet_pk, athlete__team__pk=team_pk
    ):
        entries_by_event[individual_entry.event].append(individual_entry)
    for relay_entry in MeetRelayEntry.objects.filter(
        meet__pk=meet_pk, athlete_1__team__pk=team_pk
    ):
        entries_by_event[relay_entry.event].append(relay_entry)
    return entries_by_event


def _create_event_section(
    team_pk: int, entries_by_event: dict[Event, list[MeetEntry]], event: Event
) -> Section:
    if event in INDIVIDUAL_EVENTS:
        return _create_individual_event_section(team_pk, entries_by_event[event], event)
    elif event in RELAY_EVENTS:
        return _create_relay_event_section(team_pk, entries_by_event[event], event)


def _create_individual_event_section(
    team_pk: int, entries_for_event: list[MeetEntry], event: Event
) -> Section:
    forms = []
    for i in range(ENTRIES_PER_EVENT):
        prefix = f"{event.as_prefix()}-{i}"
        try:
            entry = entries_for_event[i]
            initial = {
                "athlete": entry.athlete.pk,
                "seed": entry.seed,
            }
        except IndexError:
            initial = {}
        forms.append(
            MeetAthleteIndividualEntryForm(
                team_pk,
                prefix=prefix,
                initial=initial,
            )
        )
    return {"event": event, "forms": forms, "count": ENTRIES_PER_EVENT}


def _create_relay_event_section(
    team_pk: int, entries_for_event: list[MeetEntry], event: Event
) -> Section:
    forms = []
    for i in range(ENTRIES_PER_EVENT):
        prefix = f"{event.as_prefix()}-{i}"
        try:
            entry = entries_for_event[i]
            initial = {
                "athlete_1": entry.athlete_1.pk,
                "athlete_2": entry.athlete_2.pk,
                "athlete_3": entry.athlete_3.pk,
                "athlete_4": entry.athlete_4.pk,
                "seed": entry.seed,
            }
        except IndexError:
            initial = {}
        forms.append(
            MeetAthleteRelayEntryForm(
                team_pk,
                prefix=prefix,
                initial=initial,
            )
        )
    return {"event": event, "forms": forms, "count": ENTRIES_PER_EVENT}


@login_required
@require_http_methods(["POST"])
def save_meet_entries_for_team(
    request: HttpRequest, meet_pk: int, team_pk: int
) -> HttpResponse:
    _validate_request(request.user, meet_pk, team_pk)

    entries = MeetIndividualEntry.objects.filter(
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
                    MeetIndividualEntry.objects.create(
                        meet_id=meet_pk,
                        athlete_id=int(athlete_pk),
                        event=event,
                        seed=Decimal(seed),
                    )
                else:
                    MeetIndividualEntry.objects.create(
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
