from __future__ import annotations

import itertools
from collections import defaultdict
from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from common.constants import EVENT_ORDER, INDIVIDUAL_EVENTS, RELAY_EVENTS
from common.models import Meet, Team
from registration.constants import ENTRIES_PER_EVENT
from registration.forms import (
    MeetEntryForm,
    MeetIndividualEntryForm,
    MeetRelayEntryForm,
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
    from registration.models import MeetEntry

from typing import TypedDict


class Section(TypedDict):
    event: Event
    count: int
    forms: list[MeetEntryForm]


@login_required
@require_http_methods(["GET", "POST"])
def meet_entries_for_team(
    request: HttpRequest, meet_pk: int, team_pk: int
) -> HttpResponse:
    _validate_request(request.user, meet_pk, team_pk)
    athlete_choices = list(Athlete.objects.filter(team__pk=team_pk, active=True))

    sections = []
    entries_by_event_by_order = _read_entries_by_event_by_order(meet_pk, team_pk)
    for event in EVENT_ORDER:
        sections.append(
            _build_event_section(
                request, event, entries_by_event_by_order[event], athlete_choices
            )
        )
    if request.method == "POST":
        _update_entries(meet_pk, team_pk, sections, entries_by_event_by_order)
        if not any(form.errors for section in sections for form in section["forms"]):
            return redirect("meet entries", meet_pk=meet_pk, team_pk=team_pk)

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


def _read_entries_by_event_by_order(
    meet_pk: int, team_pk: int
) -> dict[Event, dict[int, MeetEntry]]:
    entries_by_event_by_order = defaultdict(lambda: {})
    for entry in itertools.chain(
        MeetIndividualEntry.objects.filter(meet__pk=meet_pk, team__pk=team_pk),
        MeetRelayEntry.objects.filter(meet__pk=meet_pk, team__pk=team_pk),
    ):
        entries_by_event_by_order[entry.event][entry.order] = entry
    return entries_by_event_by_order


def _build_event_section(
    request: HttpRequest,
    event: Event,
    entries_by_order: dict[int, MeetEntry],
    athlete_choices: list[Athlete],
) -> Section:
    forms = [
        _build_event_entry_form(
            request, event, entries_by_order, athlete_choices, index
        )
        for index in range(ENTRIES_PER_EVENT)
    ]
    return {"event": event, "forms": forms, "count": ENTRIES_PER_EVENT}


def _build_event_entry_form(
    request: HttpRequest,
    event: Event,
    entries_by_order: dict[int, MeetEntry],
    athlete_choices: list[Athlete],
    index: int,
) -> MeetEntryForm:
    prefix = f"{event.as_prefix()}-{index}"

    if event in INDIVIDUAL_EVENTS:
        form_class = MeetIndividualEntryForm
    elif event in RELAY_EVENTS:
        form_class = MeetRelayEntryForm

    if request.method == "POST":
        return form_class(athlete_choices, request.POST, prefix=prefix)

    initial = {"order": index}
    if index not in entries_by_order:
        return form_class(athlete_choices, prefix=prefix, initial=initial)

    entry = entries_by_order[index]
    if event in INDIVIDUAL_EVENTS:
        initial.update(
            {
                "athlete": entry.athlete.pk,
                "seed": entry.seed,
            }
        )
    elif event in RELAY_EVENTS:
        initial.update(
            {
                "athlete_0": entry.athlete_0.pk,
                "athlete_1": entry.athlete_1.pk,
                "athlete_2": entry.athlete_2.pk,
                "athlete_3": entry.athlete_3.pk,
                "seed": entry.seed,
            }
        )

    return form_class(athlete_choices, prefix=prefix, initial=initial)


def _update_entries(
    meet_pk: int,
    team_pk: int,
    sections: list[Section],
    entries_by_event_by_order: dict[Event, dict[int, MeetEntry]],
) -> None:
    for section in sections:
        event = section["event"]
        for index, form in enumerate(section["forms"]):
            form.full_clean()
            if not form.is_valid() or _is_form_empty(event, form):
                entries_by_event_by_order[event].pop(index, None)
                continue

            current_entry = entries_by_event_by_order[event].get(index)
            if current_entry:
                _update_entry(event, current_entry, form)
                entries_by_event_by_order[event].pop(index)
            else:
                entry = _create_entry(meet_pk, team_pk, event, index, form)
                try:
                    entry.full_clean()
                    entry.save()
                except ValidationError as e:
                    form.add_error(None, e)

    for entry in itertools.chain.from_iterable(
        entries_by_athlete_pks.values()
        for entries_by_athlete_pks in entries_by_event_by_order.values()
    ):
        entry.delete()


INDIVIDUAL_EVENT_FORM_FIELDS = ["athlete", "seed"]
RELAY_EVENT_FORM_FIELDS = ["athlete_0", "athlete_1", "athlete_2", "athlete_3", "seed"]


def _is_form_empty(event: Event, form: MeetEntryForm) -> bool:
    if event in INDIVIDUAL_EVENTS:
        fields = INDIVIDUAL_EVENT_FORM_FIELDS
    elif event in RELAY_EVENTS:
        fields = RELAY_EVENT_FORM_FIELDS

    return all(form.cleaned_data[field] is None for field in fields)


def _update_entry(event: Event, entry: MeetEntry, form: MeetEntryForm) -> None:
    if event in INDIVIDUAL_EVENTS:
        entry.athlete_id = form.cleaned_data["athlete"]
    elif event in RELAY_EVENTS:
        entry.athlete_0_id = form.cleaned_data["athlete_0"]
        entry.athlete_1_id = form.cleaned_data["athlete_1"]
        entry.athlete_2_id = form.cleaned_data["athlete_2"]
        entry.athlete_3_id = form.cleaned_data["athlete_3"]
    entry.seed = form.cleaned_data["seed"]
    entry.save()


def _create_entry(
    meet_pk: int, team_pk: int, event: Event, index: int, form: MeetEntryForm
) -> MeetEntry:
    if event in INDIVIDUAL_EVENTS:
        return MeetIndividualEntry(
            meet_id=meet_pk,
            team_id=team_pk,
            event=event,
            order=index,
            athlete_id=form.cleaned_data["athlete"],
            seed=form.cleaned_data["seed"],
        )
    elif event in RELAY_EVENTS:
        return MeetRelayEntry(
            meet_id=meet_pk,
            team_id=team_pk,
            event=event,
            order=index,
            athlete_0_id=form.cleaned_data["athlete_0"],
            athlete_1_id=form.cleaned_data["athlete_1"],
            athlete_2_id=form.cleaned_data["athlete_2"],
            athlete_3_id=form.cleaned_data["athlete_3"],
            seed=form.cleaned_data["seed"],
        )
