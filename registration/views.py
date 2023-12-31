from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from common.constants import EVENT_ORDER
from common.models import Coach, Meet, MeetTeam, Team
from registration.managers import MeetEntriesManager
from registration.models import Athlete

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

    from account.models import Profile


@login_required
@require_http_methods(["GET", "POST"])
def edit_meet_entries(request: HttpRequest, meet_id: int, team_id: int) -> HttpResponse:
    _validate_request(request.user, meet_id, team_id)

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
    _validate_request(request.user, meet_id, team_id)

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


def _validate_request(user: Profile, meet_id: int, team_id: int) -> None:
    if not Meet.objects.filter(id=meet_id).exists():
        raise Http404("Meet not found")
    if not Team.objects.filter(id=team_id).exists():
        raise Http404("Team not found")
    if not MeetTeam.objects.filter(meet__id=meet_id, team__id=team_id).exists():
        raise Http404("Team not registered to meet")

    if user.is_superuser:
        return
    team_ids = Coach.objects.filter(profile=user).values_list("team__id", flat=True)
    if team_id not in team_ids:
        raise PermissionDenied("User is not registered to the team")
