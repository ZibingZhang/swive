from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.middleware import csrf

from common.tables.paginator import TableColumn

if TYPE_CHECKING:
    from registration.models import CoachRequest
    from common.models import Meet, Team


def _process_coach_request_builder(coach_request: CoachRequest, context: dict) -> str:
    request = context["request"]
    approve = context["approve"]
    return f"""
        <div class="position-relative text-center">
            <form action="{request.build_absolute_uri()}" method="post" name="{approve}">
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf.get_token(request)}">
                <input type="submit" class="btn {'btn-success' if approve else 'btn-danger'}" value="{'Approve' if approve else 'Deny'}">
                <input type="hidden" name="team_id" value="{coach_request.team.id}">
                <input type="hidden" name="profile_id" value="{coach_request.profile.id}">
                <input type="hidden" name="approve" value="{approve}">
            </form>
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
                View Registered Teams ({meet.teams.all().count()})
            </a>
        </div"""


def _team_coach_status_builder(team: Team, context: dict) -> str:
    request = context["request"]
    button_class = "btn-success"
    button_text = "Join Team"
    disabled = False
    if team in request.user.teams.all():
        disabled = True
        button_text = "Joined"
    if team.id in request.user.coach_requests.all().values_list("team", flat=True):
        button_class = "btn-danger"
        button_text = "Requested"
    return f"""
        <div class="position-relative text-center">
            <form action="{request.build_absolute_uri()}" method="post">
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf.get_token(request)}">
                <input type="submit" class="btn {button_class}" value="{button_text}" {'disabled' if disabled else ''}>
                <input type="hidden" name="team_id" value="{team.id}">
            </form>
        </div"""


class Column:
    END_DATE = TableColumn("End Date", field="end_date")
    ENTRIES = TableColumn("Entries", builder=_entries_builder)
    NAME = TableColumn("Name", field="name")
    PROCESS_COACH_REQUEST = TableColumn("", builder=_process_coach_request_builder)
    PROFILE = TableColumn("Profile", field="profile")
    REGISTERED_MEETS = TableColumn(
        "Registered Meets", builder=_registered_meets_builder
    )
    REGISTERED_TEAMS = TableColumn(
        "Registered Teams", builder=_registered_teams_builder
    )
    START_DATE = TableColumn("Start Date", field="start_date")
    TEAM = TableColumn("Team", field="team")
    TEAM_COACH_STATUS = TableColumn(
        "Join Team Request", builder=_team_coach_status_builder
    )
