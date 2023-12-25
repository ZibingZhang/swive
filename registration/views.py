from __future__ import annotations

import itertools
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
from common.utils import is_seed, seed_to_decimal
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
@require_http_methods(["GET", "POST"])
def meet_entries_for_team(
    request: HttpRequest, meet_pk: int, team_pk: int
) -> HttpResponse:
    _validate_request(request.user, meet_pk, team_pk)

    sections = []
    entries_by_event = _query_entries_by_event(meet_pk, team_pk)
    if request.method == "POST":
        entries_by_event_athlete_pk = {}
        for entry in itertools.chain.from_iterable(entries_by_event.values()):
            if isinstance(entry, MeetIndividualEntry):
                entries_by_event_athlete_pk[
                    (entry.event, str(entry.athlete.pk))
                ] = entry
        entries_by_event = _update_entries_by_event(
            entries_by_event_athlete_pk, meet_pk, request.POST
        )
    for event in EVENT_ORDER:
        sections.append(_create_event_section(team_pk, entries_by_event, event))
    return render(request, "meet-entry.html", {"sections": sections})


def _query_entries_by_event(meet_pk: int, team_pk: int) -> dict[Event, list[MeetEntry]]:
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


def _update_entries_by_event(
    entries_by_event_athlete_pk: dict[tuple[Event, int], MeetEntry],
    meet_pk: int,
    body: dict,
) -> dict[Event, list[MeetEntry]]:
    entries_by_event = defaultdict(lambda: [])
    errors = []
    for event in INDIVIDUAL_EVENTS:
        for i in range(ENTRIES_PER_EVENT):
            try:
                athlete_pk_value = body[f"{event.as_prefix()}-{i}-athlete"]
                seed_value = body[f"{event.as_prefix()}-{i}-seed"]
            except KeyError:
                continue
            if athlete_pk_value == "":
                if seed_value != "":
                    errors.append("Missing athlete")
                continue
            try:
                athlete_pk = int(athlete_pk_value)
            except ValueError:
                continue
            if seed_value != "" and not is_seed(seed_value):
                errors.append("Invalid seed")
                continue
            seed = None if seed_value == "" else seed_to_decimal(seed_value)
            entry = entries_by_event_athlete_pk.get((event, athlete_pk))
            if entry:
                entry.seed = seed
                entry.save()
                entries_by_event_athlete_pk.pop((event, athlete_pk))
            else:
                entry = MeetIndividualEntry.objects.create(
                    meet_id=meet_pk, athlete_id=int(athlete_pk), event=event, seed=seed
                )

            entries_by_event[event].append(entry)
    for entry in entries_by_event_athlete_pk.values():
        entry.delete()
    return entries_by_event


def _create_event_section(
    team_pk: int, entries_by_event: dict[Event, list[MeetEntry]], event: Event
) -> Section:
    if event in INDIVIDUAL_EVENTS:
        return _create_individual_event_section(team_pk, entries_by_event[event], event)
    elif event in RELAY_EVENTS:
        return _create_relay_event_section(team_pk, entries_by_event[event], event)


def _create_individual_event_section(
    team_pk: int, entries_for_event: list[MeetIndividualEntry], event: Event
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
    team_pk: int, entries_for_event: list[MeetRelayEntry], event: Event
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
