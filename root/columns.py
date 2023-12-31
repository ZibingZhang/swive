from __future__ import annotations

from typing import TYPE_CHECKING, Any

from common.paginator import TableColumn

if TYPE_CHECKING:
    from common.models import Meet, Team


def _registered_meets_builder(team: Team) -> str:
    return f"""
        <div class="position-relative text-center">
            <a href="/team/{ team.id }/meets" class="btn btn-secondary link-light stretched-link text-decoration-none">
                View Registered Meets
            </a>
        </div"""


def _registered_teams_builder(meet: Meet) -> str:
    return f"""
        <div class="position-relative text-center">
            <a href="/meet/{ meet.id }/teams" class="btn btn-secondary link-light stretched-link text-decoration-none">
                View Registered Teams
            </a>
        </div"""


def _entries_builder(obj: Any, context: dict) -> str:
    editable_ids = context["editable_ids"]
    if obj.id not in editable_ids:
        return ""
    meet_team_ids = context["meet_team_ids_map"][obj.id]
    return f"""
        <div class="position-relative text-center">
            <a href="/registration/entries/meet/{meet_team_ids[0]}/team/{meet_team_ids[1]}/edit" class="btn btn-secondary link-light stretched-link text-decoration-none">
                View Entries
            </a>
        </div"""


class Column:
    END_DATE = TableColumn("End Date", field="end_date")
    NAME = TableColumn("Name", field="name")
    START_DATE = TableColumn("Start Date", field="start_date")
    REGISTERED_MEETS = TableColumn(
        "Registered Meets", builder=_registered_meets_builder
    )
    REGISTERED_TEAMS = TableColumn(
        "Registered Teams", builder=_registered_teams_builder
    )
    ENTRIES = TableColumn("Entries", builder=_entries_builder)
