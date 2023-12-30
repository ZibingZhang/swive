from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from django.contrib.auth.decorators import login_required

from common.admin import MeetAdmin, TeamAdmin
from common.models import BaseModel, Meet, Team
from common.paginator import PaginatedSearchRenderer
from registration.models import CoachEntry, MeetTeamEntry
from root.columns import Column

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

M = TypeVar("M", bound=BaseModel)


def all_meets(request: HttpRequest) -> HttpResponse:
    columns = [
        Column.NAME,
        Column.START_DATE,
        Column.END_DATE,
        Column.REGISTERED_TEAMS,
    ]
    renderer = PaginatedSearchRenderer(request, Meet, MeetAdmin, "All Meets", columns)
    return renderer.render()


def teams_for_meet(request: HttpRequest, meet_pk: int) -> HttpResponse:
    columns = [Column.NAME, Column.REGISTERED_MEETS]
    meet_name = Meet.objects.filter(id=meet_pk).get().name
    team_pks = MeetTeamEntry.objects.filter(meet__id=meet_pk).values_list(
        "team__id", flat=True
    )
    renderer = PaginatedSearchRenderer(
        request, Team, TeamAdmin, f"{meet_name} Teams", columns
    )
    renderer.objects = renderer.objects.filter(id__in=team_pks)
    return renderer.render()


def all_teams(request: HttpRequest) -> HttpResponse:
    columns = [Column.NAME, Column.REGISTERED_MEETS]
    renderer = PaginatedSearchRenderer(request, Team, TeamAdmin, "All Meets", columns)
    return renderer.render()


@login_required
def my_teams(request: HttpRequest) -> HttpResponse:
    columns = [Column.NAME, Column.REGISTERED_MEETS]
    renderer = PaginatedSearchRenderer(request, Team, TeamAdmin, "My Teams", columns)
    team_pks = CoachEntry.objects.filter(profile=request.user).values_list(
        "team__id", flat=True
    )
    renderer.objects = renderer.objects.filter(id__in=team_pks)
    return renderer.render()


def meets_for_team(request: HttpRequest, team_pk: int) -> HttpResponse:
    columns = [
        Column.NAME,
        Column.START_DATE,
        Column.END_DATE,
        Column.REGISTERED_TEAMS,
    ]
    team_name = Team.objects.filter(id=team_pk).get().name
    meet_pks = MeetTeamEntry.objects.filter(team__id=team_pk).values_list(
        "meet__id", flat=True
    )
    renderer = PaginatedSearchRenderer(
        request, Meet, MeetAdmin, f"{team_name} Meets", columns
    )
    renderer.objects = renderer.objects.filter(id__in=meet_pks)
    return renderer.render()
