from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from common.admin import TeamAdmin
from common.tables.paginator import PaginatedSearchRenderer
from common.constants import EVENT_ORDER
from common.models import Meet, Team, Coach
from common.tables.columns import Column
from registration.admin import CoachRequestAdmin
from registration.managers import MeetEntriesManager
from registration.models import Athlete, CoachRequest
from django.http import Http404

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


@login_required
@require_http_methods(["GET", "POST"])
def edit_meet_entries(request: HttpRequest, meet_id: int, team_id: int) -> HttpResponse:
    MeetEntriesManager.validate_request(request.user, meet_id, team_id)

    meet = Meet.objects.filter(id=meet_id).get()
    team = Team.objects.filter(id=team_id).get()

    if not meet.entries_open:
        return redirect("view meet entries", meet_id=meet_id, team_id=team_id)

    athlete_choices = list(Athlete.objects.filter(team__id=team_id, active=True))
    entries_by_event_by_order = MeetEntriesManager.read_entries_by_event_by_order(
        meet_id, team_id
    )
    sections = MeetEntriesManager.build_event_sections(
        request, EVENT_ORDER, entries_by_event_by_order, athlete_choices
    )

    if request.method == "POST":
        MeetEntriesManager.update_entries(
            meet_id, team_id, sections, entries_by_event_by_order
        )
        if not any(form.errors for section in sections for form in section["forms"]):
            return redirect("edit meet entries", meet_id=meet_id, team_id=team_id)

    return render(
        request,
        "meet-entries.html",
        {
            "meet_name": meet.name,
            "team_name": team.name,
            "sections": sections,
            "view_only": False,
            "meet_id": meet_id,
            "team_id": team_id,
        },
    )


@login_required
@require_http_methods(["GET"])
def view_meet_entries(request: HttpRequest, meet_id: int, team_id: int) -> HttpResponse:
    MeetEntriesManager.validate_request(request.user, meet_id, team_id)

    meet = Meet.objects.filter(id=meet_id).get()
    team = Team.objects.filter(id=team_id).get()

    athlete_choices = list(Athlete.objects.filter(team__id=team_id, active=True))
    entries_by_event_by_order = MeetEntriesManager.read_entries_by_event_by_order(
        meet_id, team_id
    )
    sections = MeetEntriesManager.build_event_sections(
        request, EVENT_ORDER, entries_by_event_by_order, athlete_choices
    )

    for section in sections:
        for form in section["forms"]:
            for key in form.fields.keys():
                form.fields[key].disabled = True

    return render(
        request,
        "meet-entries.html",
        {
            "meet_name": meet.name,
            "team_name": team.name,
            "sections": sections,
            "view_only": True,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def team_coach_status(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        qs = CoachRequest.objects.filter(
            profile=request.user, team_id=request.POST["team_id"]
        )
        if qs.exists():
            qs.delete()
        else:
            CoachRequest.objects.create(
                profile=request.user, team_id=request.POST["team_id"]
            )
        return redirect(reverse("team coach status") + "?" + request.GET.urlencode())

    columns = [
        Column.NAME,
        Column.TEAM_COACH_STATUS.with_context({"request": request}),
    ]

    renderer = PaginatedSearchRenderer(request, Team, TeamAdmin, "Join a Team", columns)
    return renderer.render()


@login_required
@require_http_methods(["GET", "POST"])
def coach_requests(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        team_id = int(request.POST["team_id"])
        profile_id = int(request.POST["profile_id"])
        approve = request.POST["approve"] == "True"
        qs = CoachRequest.objects.filter(team_id=team_id, profile_id=profile_id)
        if not qs.exists():
            raise Http404("Coach request not found")
        if Coach.objects.filter(team_id=team_id, profile_id=profile_id).exists():
            return redirect("coach requests")
        if approve:
            Coach.objects.create(team_id=team_id, profile_id=profile_id)
        qs.get().delete()
        return redirect("coach requests")

    columns = [
        Column.TEAM,
        Column.PROFILE,
        Column.PROCESS_COACH_REQUEST.with_header("Approve").with_context({"request": request, "approve": True}),
        Column.PROCESS_COACH_REQUEST.with_header("Deny").with_context({"request": request, "approve": False}),
    ]

    renderer = PaginatedSearchRenderer(request, CoachRequest, CoachRequestAdmin, "Coach Requests", columns)
    return renderer.render()
