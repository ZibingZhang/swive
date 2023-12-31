from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from django.contrib.auth.decorators import login_required

from common.admin import MeetAdmin, TeamAdmin
from common.models import Meet, SoftDeleteModel, Team, Coach
from common.paginator import PaginatedSearchRenderer
from common.models import MeetTeam
from root.columns import Column

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

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
    columns = [Column.NAME, Column.REGISTERED_MEETS]
    meet_name = Meet.objects.filter(id=meet_id).get().name
    team_ids = MeetTeam.objects.filter(meet__id=meet_id).values_list(
        "team_id", flat=True
    )
    renderer = PaginatedSearchRenderer(
        request, Team, TeamAdmin, f"{meet_name} Teams", columns
    )
    renderer.objects = renderer.objects.filter(id__in=team_ids)

    if request.user.is_authenticated and request.user.is_coach:
        coach_team_ids = Coach.objects.filter(profile=request.user).values_list(
            "team_id", flat=True
        )
        meet_team_ids_map = {}
        for team_id in coach_team_ids:
            meet_team_ids_map[team_id] = (meet_id, team_id)
        renderer.columns.append(
            Column.ENTRIES.with_context(
                {"editable_ids": coach_team_ids, "meet_team_ids_map": meet_team_ids_map}
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
    team_ids = Coach.objects.filter(profile=request.user).values_list(
        "team_id", flat=True
    )
    renderer.objects = renderer.objects.filter(id__in=team_ids)
    return renderer.render()


def meets_for_team(request: HttpRequest, team_id: int) -> HttpResponse:
    columns = [
        Column.NAME,
        Column.START_DATE,
        Column.END_DATE,
        Column.REGISTERED_TEAMS,
    ]
    team_name = Team.objects.filter(id=team_id).get().name
    meet_ids = MeetTeam.objects.filter(team_id=team_id).values_list(
        "meet_id", flat=True
    )
    renderer = PaginatedSearchRenderer(
        request, Meet, MeetAdmin, f"{team_name} Meets", columns
    )
    renderer.objects = renderer.objects.filter(id__in=meet_ids)

    if (
        request.user.is_authenticated
        and request.user.is_coach
        and Coach.objects.filter(profile=request.user, team_id=team_id).exists()
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
