from __future__ import annotations

import itertools
from collections import defaultdict
from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from common.constants import EVENT_ORDER, INDIVIDUAL_EVENTS, RELAY_EVENTS
from common.models import Meet, Team
from registration.constants import ENTRIES_PER_EVENT
from registration.forms import AthleteForm, MeetIndividualEntryForm, MeetRelayEntryForm
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
    from common.forms import BaseForm
    from registration.models import MeetEntry

from typing import TypedDict


class Section(TypedDict):
    event: Event
    count: int
    forms: list[BaseForm]


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
    athlete_choices = list(Athlete.objects.filter(team__pk=team_pk))

    sections = []
    entries_by_event = _read_entries_by_event(meet_pk, team_pk)
    for event in EVENT_ORDER:
        sections.append(
            _build_event_section(request, event, entries_by_event, athlete_choices)
        )
    if request.method == "POST":
        entries_by_event_by_athlete_pks = defaultdict(lambda: {})
        for entry in itertools.chain.from_iterable(entries_by_event.values()):
            if isinstance(entry, MeetIndividualEntry):
                athlete_pks = (entry.athlete.pk,)
            elif isinstance(entry, MeetRelayEntry):
                athlete_pks = (
                    entry.athlete_1.pk,
                    entry.athlete_2.pk,
                    entry.athlete_3.pk,
                    entry.athlete_4.pk,
                )
            entries_by_event_by_athlete_pks[entry.event][athlete_pks] = entry
        _update_entries(meet_pk, sections, entries_by_event_by_athlete_pks)

    return render(request, "meet-entry.html", {"sections": sections})


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


def _read_entries_by_event(meet_pk: int, team_pk: int) -> dict[Event, list[MeetEntry]]:
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


def _build_event_section(
    request: HttpRequest,
    event: Event,
    entries_by_event: dict[Event, list[MeetEntry]],
    athlete_choices: list[Athlete],
) -> Section:
    if event in INDIVIDUAL_EVENTS:
        return _build_individual_event_section(
            request, event, entries_by_event[event], athlete_choices
        )
    elif event in RELAY_EVENTS:
        return _build_relay_event_section(
            request, event, entries_by_event[event], athlete_choices
        )


def _build_individual_event_section(
    request: HttpRequest,
    event: Event,
    entries_for_event: list[MeetIndividualEntry],
    athlete_choices: list[Athlete],
) -> Section:
    forms = [
        _build_individual_event_entry_form(
            request, event, entries_for_event, athlete_choices, index
        )
        for index in range(ENTRIES_PER_EVENT)
    ]
    return {"event": event, "forms": forms, "count": ENTRIES_PER_EVENT}


def _build_individual_event_entry_form(
    request: HttpRequest,
    event: Event,
    entries_for_event: list[MeetIndividualEntry],
    athlete_choices: list[Athlete],
    index: int,
) -> MeetIndividualEntryForm:
    prefix = f"{event.as_prefix()}-{index}"

    if request.method == "POST":
        return MeetIndividualEntryForm(athlete_choices, request.POST, prefix=prefix)

    try:
        entry = entries_for_event[index]
        initial = {
            "athlete": entry.athlete.pk,
            "seed": entry.seed,
        }
    except IndexError:
        initial = {}

    return MeetIndividualEntryForm(
        athlete_choices,
        prefix=prefix,
        initial=initial,
    )


def _build_relay_event_section(
    request: HttpRequest,
    event: Event,
    entries_for_event: list[MeetRelayEntry],
    athlete_choices: list[Athlete],
) -> Section:
    forms = [
        _build_relay_event_entry_form(
            request, event, entries_for_event, athlete_choices, index
        )
        for index in range(ENTRIES_PER_EVENT)
    ]
    return {"event": event, "forms": forms, "count": ENTRIES_PER_EVENT}


def _build_relay_event_entry_form(
    request: HttpRequest,
    event: Event,
    entries_for_event: list[MeetRelayEntry],
    athlete_choices: list[Athlete],
    index: int,
) -> MeetRelayEntryForm:
    prefix = f"{event.as_prefix()}-{index}"

    if request.method == "POST":
        return MeetRelayEntryForm(athlete_choices, request.POST, prefix=prefix)

    try:
        entry = entries_for_event[index]
        initial = {
            "athlete_1": entry.athlete_1.pk,
            "athlete_2": entry.athlete_2.pk,
            "athlete_3": entry.athlete_3.pk,
            "athlete_4": entry.athlete_4.pk,
            "seed": entry.seed,
        }
    except IndexError:
        initial = {}
    return MeetRelayEntryForm(
        athlete_choices,
        prefix=prefix,
        initial=initial,
    )


def _update_entries(
    meet_pk: int,
    sections: list[Section],
    entries_by_event_by_athlete_pks: dict[Event, dict[tuple[int, ...]], MeetEntry],
) -> None:
    for section in sections:
        event = section["event"]
        for form in section["forms"]:
            form.full_clean()

            if event in INDIVIDUAL_EVENTS:
                athlete_pks = (form.cleaned_data.get("athlete"),)
            elif event in RELAY_EVENTS:
                athlete_pks = (
                    form.cleaned_data.get("athlete_1"),
                    form.cleaned_data.get("athlete_2"),
                    form.cleaned_data.get("athlete_3"),
                    form.cleaned_data.get("athlete_4"),
                )
            if any(athlete_pk is None for athlete_pk in athlete_pks):
                continue

            current_entry = entries_by_event_by_athlete_pks[event].get(athlete_pks)
            seed = form.cleaned_data.get("seed")

            if current_entry:
                current_entry.seed = seed
                current_entry.save()
                entries_by_event_by_athlete_pks[event].pop(athlete_pks)
            else:
                if event in INDIVIDUAL_EVENTS:
                    entry = MeetIndividualEntry(
                        meet_id=meet_pk,
                        athlete_id=athlete_pks[0],
                        event=event,
                        seed=seed,
                    )
                    try:
                        entry.full_clean()
                        entry.save()
                    except ValidationError as e:
                        form.add_error(None, e)
                elif event in RELAY_EVENTS:
                    entry = MeetRelayEntry(
                        meet_id=meet_pk,
                        athlete_1_id=athlete_pks[0],
                        athlete_2_id=athlete_pks[1],
                        athlete_3_id=athlete_pks[2],
                        athlete_4_id=athlete_pks[3],
                        event=event,
                        seed=seed,
                    )
                    try:
                        entry.full_clean()
                        entry.save()
                    except ValidationError as e:
                        form.add_error(None, e)

    for entry in itertools.chain.from_iterable(
        entries_by_athlete_pks.values()
        for entries_by_athlete_pks in entries_by_event_by_athlete_pks.values()
    ):
        entry.delete()
