from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from django.contrib.auth.decorators import login_required

from common.admin import MeetAdmin, TeamAdmin
from common.models import Meet, MeetTeam, SoftDeleteModel, Team
from common.paginator import PaginatedSearchRenderer
from root.columns import Column

if TYPE_CHECKING:
    from django.http import Http404, HttpRequest, HttpResponse

M = TypeVar("M", bound=SoftDeleteModel)


def all_meets(request: HttpRequest) -> HttpResponse:
    columns = [
        Column.NAME,
        Column.START_DATE,
        Column.END_DATE,
        Column.REGISTERED_TEAMS,
    ]
    renderer = PaginatedSearchRenderer(request, Meet, MeetAdmin, "All Meets", columns)
    return renderer.render()


def teams_for_meet(request: HttpRequest, meet_id: int) -> HttpResponse:
    if not Meet.objects.filter(id=meet_id).exists():
        raise Http404("Meet not found")

    columns = [Column.NAME, Column.REGISTERED_MEETS]
    meet = Meet.objects.filter(id=meet_id).get()
    renderer = PaginatedSearchRenderer(
        request, Team, TeamAdmin, f"{meet.name} Teams", columns
    )
    renderer.objects = meet.teams.all()

    if request.user.is_authenticated and request.user.is_coach:
        meet_team_ids_map = {}
        team_ids = request.user.teams.all().values_list("id", flat=True)
        for team_id in team_ids:
            meet_team_ids_map[team_id] = (meet_id, team_id)
        renderer.columns.append(
            Column.ENTRIES.with_context(
                {"editable_ids": team_ids, "meet_team_ids_map": meet_team_ids_map}
            )
        )

    return renderer.render()


def all_teams(request: HttpRequest) -> HttpResponse:
    columns = [Column.NAME, Column.REGISTERED_MEETS]
    renderer = PaginatedSearchRenderer(request, Team, TeamAdmin, "All Teams", columns)
    return renderer.render()


@login_required
def my_teams(request: HttpRequest) -> HttpResponse:
    columns = [Column.NAME, Column.REGISTERED_MEETS]
    renderer = PaginatedSearchRenderer(request, Team, TeamAdmin, "My Teams", columns)
    renderer.objects = request.user.teams.all()
    return renderer.render()


def meets_for_team(request: HttpRequest, team_id: int) -> HttpResponse:
    if not Team.objects.filter(id=team_id).exists():
        raise Http404("Team not found")

    columns = [
        Column.NAME,
        Column.START_DATE,
        Column.END_DATE,
        Column.REGISTERED_TEAMS,
    ]
    team = Team.objects.filter(id=team_id).get()
    meet_ids = MeetTeam.objects.filter(team_id=team_id).values_list(
        "meet_id", flat=True
    )
    renderer = PaginatedSearchRenderer(
        request, Meet, MeetAdmin, f"{team.name} Meets", columns
    )
    renderer.objects = team.meets.all()

    if (
        request.user.is_authenticated
        and request.user.is_coach
        and request.user.teams.all().filter(id=team_id).exists()
    ):
        meet_team_ids_map = {}
        for meet in renderer.objects:
            meet_team_ids_map[meet.id] = (meet.id, team_id)
        renderer.columns.append(
            Column.ENTRIES.with_context(
                {"editable_ids": meet_ids, "meet_team_ids_map": meet_team_ids_map}
            )
        )

    return renderer.render()
