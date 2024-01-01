from __future__ import annotations

import itertools
from collections import defaultdict
from typing import TYPE_CHECKING, TypedDict

from django.core.exceptions import ValidationError

from common.constants import INDIVIDUAL_EVENTS, RELAY_EVENTS
from common.models import Athlete
from registration.constants import ENTRIES_PER_INDIVIDUAL_EVENT, ENTRIES_PER_RELAY_EVENT
from registration.forms import MeetIndividualEntryForm, MeetRelayEntryForm
from registration.models import MeetIndividualEntry, MeetRelayEntry

if TYPE_CHECKING:
    from django.http import HttpRequest

    from common.constants import Event
    from registration.forms import MeetEntryForm
    from registration.models import MeetEntry


class Section(TypedDict):
    event: Event
    count: int
    forms: list[MeetEntryForm]


class MeetEntriesManager:
    INDIVIDUAL_EVENT_ATHLETE_FIELDS = ["athlete"]
    RELAY_EVENT_ATHLETE_FIELDS = ["athlete_0", "athlete_1", "athlete_2", "athlete_3"]
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
        meet_id: int, team_id: int
    ) -> dict[Event, dict[int, MeetEntry]]:
        entries_by_event_by_order = defaultdict(lambda: {})
        for entry in itertools.chain(
            MeetIndividualEntry.objects.filter(meet__id=meet_id, team__id=team_id),
            MeetRelayEntry.objects.filter(meet__id=meet_id, team__id=team_id),
        ):
            entries_by_event_by_order[entry.event][entry.order] = entry
        return entries_by_event_by_order

    @staticmethod
    def build_event_sections(
        request: HttpRequest,
        events: list[Event],
        entries_by_event_by_order: dict[Event, dict[int, MeetEntry]],
        athlete_choices: list[Athlete],
    ) -> list[Section]:
        sections = []
        for event in events:
            sections.append(
                MeetEntriesManager._build_event_section_for_editing(
                    request, event, entries_by_event_by_order[event], athlete_choices
                )
            )
        return sections

    @staticmethod
    def _build_event_section_for_editing(
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
        return Section(event=event, count=count, forms=forms)

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
            return form_class(athlete_choices, request.POST, prefix=prefix, event=event)

        initial = {"order": index}
        if index not in entries_by_order:
            return form_class(
                athlete_choices, prefix=prefix, initial=initial, event=event
            )

        entry = entries_by_order[index]
        if event in INDIVIDUAL_EVENTS:
            initial.update(
                {
                    "athlete": entry.athlete.id,
                    "seed": entry.seed,
                }
            )
        elif event in RELAY_EVENTS:
            initial.update(
                {
                    "athlete_0": entry.athlete_0.id,
                    "athlete_1": entry.athlete_1.id,
                    "athlete_2": entry.athlete_2.id,
                    "athlete_3": entry.athlete_3.id,
                    "seed": entry.seed,
                }
            )

        return form_class(athlete_choices, prefix=prefix, initial=initial, event=event)

    @staticmethod
    def update_entries(
        meet_id: int,
        team_id: int,
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
                if MeetEntriesManager._is_missing_athletes(event, form):
                    entries_by_event_by_order[event].pop(index, None)
                    continue

                current_entry = entries_by_event_by_order[event].get(index)
                if current_entry:
                    MeetEntriesManager._update_entry(event, current_entry, form)
                    entries_by_event_by_order[event].pop(index)
                else:
                    entry = MeetEntriesManager._create_entry(
                        meet_id, team_id, event, index, form
                    )
                    try:
                        entry.full_clean()
                        entry.save()
                    except ValidationError as e:
                        form.add_error(None, e)

        for entry in itertools.chain.from_iterable(
            entries_by_athlete_ids.values()
            for entries_by_athlete_ids in entries_by_event_by_order.values()
        ):
            entry.delete()

    @staticmethod
    def _is_form_empty(event: Event, form: MeetEntryForm) -> bool:
        if event in INDIVIDUAL_EVENTS:
            fields = MeetEntriesManager.INDIVIDUAL_EVENT_FORM_FIELDS
        elif event in RELAY_EVENTS:
            fields = MeetEntriesManager.RELAY_EVENT_FORM_FIELDS

        return all(form.cleaned_data[field] is None for field in fields)

    @staticmethod
    def _is_missing_athletes(event: Event, form: MeetEntryForm) -> bool:
        if event in INDIVIDUAL_EVENTS:
            fields = MeetEntriesManager.INDIVIDUAL_EVENT_ATHLETE_FIELDS
        elif event in RELAY_EVENTS:
            fields = MeetEntriesManager.RELAY_EVENT_ATHLETE_FIELDS

        missing_athlete = False
        for field in fields:
            value = form.cleaned_data[field]
            if value is None:
                missing_athlete = True
                form.add_error(field, "Missing athlete")

        return missing_athlete

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
        meet_id: int, team_id: int, event: Event, index: int, form: MeetEntryForm
    ) -> MeetEntry:
        if event in INDIVIDUAL_EVENTS:
            return MeetIndividualEntry(
                meet_id=meet_id,
                team_id=team_id,
                event=event,
                order=index,
                athlete=Athlete.objects.filter(id=form.cleaned_data["athlete"]).get(),
                seed=form.cleaned_data["seed"],
            )
        elif event in RELAY_EVENTS:
            athletes_by_id = {
                athlete.id: athlete
                for athlete in Athlete.objects.filter(
                    id__in=[
                        form.cleaned_data["athlete_0"],
                        form.cleaned_data["athlete_1"],
                        form.cleaned_data["athlete_2"],
                        form.cleaned_data["athlete_3"],
                    ]
                )
            }
            return MeetRelayEntry(
                meet_id=meet_id,
                team_id=team_id,
                event=event,
                order=index,
                athlete_0=athletes_by_id[form.cleaned_data["athlete_0"]],
                athlete_1=athletes_by_id[form.cleaned_data["athlete_1"]],
                athlete_2=athletes_by_id[form.cleaned_data["athlete_2"]],
                athlete_3=athletes_by_id[form.cleaned_data["athlete_3"]],
                seed=form.cleaned_data["seed"],
            )
