from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, Paginator
from django.shortcuts import render

from common import utils
from common.models import BaseModel, Meet, Team
from registration.models import CoachEntry, MeetTeamEntry

if TYPE_CHECKING:
    from django.core.paginator import Page
    from django.db.models import QuerySet
    from django.http import HttpRequest, HttpResponse

M = TypeVar("M", bound=BaseModel)


def all_meets(request: HttpRequest) -> HttpResponse:
    page_number = utils.as_int(request.GET.get("page"), 1)
    return render(
        request,
        "meets.html",
        {"page": _get_model_page(Meet.objects.all(), page_number)},
    )


def teams_for_meet(request: HttpRequest, meet_pk: int) -> HttpResponse:
    page_number = utils.as_int(request.GET.get("page"), 1)
    team_pks = MeetTeamEntry.objects.filter(meet__id=meet_pk).values_list(
        "team__id", flat=True
    )
    return render(
        request,
        "teams.html",
        {"page": _get_model_page(Team.objects.filter(id__in=team_pks), page_number)},
    )


def all_teams(request: HttpRequest) -> HttpResponse:
    page_number = utils.as_int(request.GET.get("page"), 1)
    return render(
        request,
        "teams.html",
        {"page": _get_model_page(Team.objects.all(), page_number)},
    )


@login_required
def my_teams(request: HttpRequest) -> HttpResponse:
    page_number = utils.as_int(request.GET.get("page"), 1)
    team_pks = CoachEntry.objects.filter(profile=request.user).values_list(
        "team__id", flat=True
    )
    return render(
        request,
        "teams.html",
        {"page": _get_model_page(Team.objects.filter(id__in=team_pks), page_number)},
    )


def _get_model_page(
    objects: QuerySet[M], page_number: int, per_page: int = 20
) -> Page[M]:
    paginator = Paginator(objects, per_page=per_page)
    page = paginator.get_page(page_number)
    try:
        page.adjusted_elided_pages = list(paginator.get_elided_page_range(page_number))
    except EmptyPage:
        page.adjusted_elided_pages = list(
            paginator.get_elided_page_range(paginator.num_pages)
        )
    return page
