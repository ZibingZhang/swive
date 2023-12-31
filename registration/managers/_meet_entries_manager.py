from __future__ import annotations

import itertools
from collections import defaultdict
from typing import TYPE_CHECKING, TypedDict

from django.core.exceptions import ValidationError

from common.constants import INDIVIDUAL_EVENTS, RELAY_EVENTS
from registration.constants import ENTRIES_PER_INDIVIDUAL_EVENT, ENTRIES_PER_RELAY_EVENT
from registration.forms import MeetIndividualEntryForm, MeetRelayEntryForm
from registration.models import MeetIndividualEntry, MeetRelayEntry

if TYPE_CHECKING:
    from django.http import HttpRequest

    from common.constants import Event
    from common.models import Athlete
    from registration.forms import MeetEntryForm
    from registration.models import MeetEntry


class Section(TypedDict):
    event: Event
    count: int
    forms: list[MeetEntryForm]


class MeetEntriesManager:
    INDIVIDUAL_EVENT_FORM_FIELDS = ["athlete", "seed"]
    RELAY_EVENT_FORM_FIELDS = [
        "athlete_0",
        "athlete_1",
        "athlete_2",
        "athlete_3",
        "seed",
    ]

    @staticmethod
    def read_entries_by_event_by_order(
        meet_pk: int, team_pk: int
    ) -> dict[Event, dict[int, MeetEntry]]:
        entries_by_event_by_order = defaultdict(lambda: {})
        for entry in itertools.chain(
            MeetIndividualEntry.objects.filter(meet__pk=meet_pk, team__pk=team_pk),
            MeetRelayEntry.objects.filter(meet__pk=meet_pk, team__pk=team_pk),
        ):
            entries_by_event_by_order[entry.event][entry.order] = entry
        return entries_by_event_by_order

    @staticmethod
    def build_event_section_for_editing(
        request: HttpRequest,
        event: Event,
        entries_by_order: dict[int, MeetEntry],
        athlete_choices: list[Athlete],
    ) -> Section:
        if event in INDIVIDUAL_EVENTS:
            count = ENTRIES_PER_INDIVIDUAL_EVENT
        elif event in RELAY_EVENTS:
            count = ENTRIES_PER_RELAY_EVENT
        forms = [
            MeetEntriesManager._build_event_entry_form(
                request, event, entries_by_order, athlete_choices, index
            )
            for index in range(count)
        ]
        return {"event": event, "forms": forms, "count": count}

    @staticmethod
    def update_entries(
        meet_pk: int,
        team_pk: int,
        sections: list[Section],
        entries_by_event_by_order: dict[Event, dict[int, MeetEntry]],
    ) -> None:
        for section in sections:
            event = section["event"]
            for index, form in enumerate(section["forms"]):
                form.full_clean()
                if not form.is_valid() or MeetEntriesManager._is_form_empty(
                    event, form
                ):
                    entries_by_event_by_order[event].pop(index, None)
                    continue

                current_entry = entries_by_event_by_order[event].get(index)
                if current_entry:
                    MeetEntriesManager._update_entry(event, current_entry, form)
                    entries_by_event_by_order[event].pop(index)
                else:
                    entry = MeetEntriesManager._create_entry(
                        meet_pk, team_pk, event, index, form
                    )
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

    @staticmethod
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

    @staticmethod
    def _is_form_empty(event: Event, form: MeetEntryForm) -> bool:
        if event in INDIVIDUAL_EVENTS:
            fields = MeetEntriesManager.INDIVIDUAL_EVENT_FORM_FIELDS
        elif event in RELAY_EVENTS:
            fields = MeetEntriesManager.RELAY_EVENT_FORM_FIELDS

        return all(form.cleaned_data[field] is None for field in fields)

    @staticmethod
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

    @staticmethod
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
