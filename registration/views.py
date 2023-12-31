from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from common.constants import EVENT_ORDER
from common.models import Meet, Team
from registration.managers import MeetEntriesManager
from registration.models import Athlete, CoachEntry, MeetTeamEntry

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

    from account.models import Profile


@login_required
@require_http_methods(["GET", "POST"])
def edit_meet_entries(request: HttpRequest, meet_pk: int, team_pk: int) -> HttpResponse:
    _validate_request(request.user, meet_pk, team_pk)

    meet = Meet.objects.filter(id=meet_pk).get()
    team = Team.objects.filter(id=team_pk).get()

    if not meet.entries_open:
        return redirect("view meet entries", meet_pk=meet_pk, team_pk=team_pk)

    athlete_choices = list(Athlete.objects.filter(team__pk=team_pk, active=True))

    sections = []
    entries_by_event_by_order = MeetEntriesManager.read_entries_by_event_by_order(
        meet_pk, team_pk
    )
    for event in EVENT_ORDER:
        sections.append(
            MeetEntriesManager.build_event_section_for_editing(
                request, event, entries_by_event_by_order[event], athlete_choices
            )
        )
    if request.method == "POST":
        MeetEntriesManager.update_entries(
            meet_pk, team_pk, sections, entries_by_event_by_order
        )
        if not any(form.errors for section in sections for form in section["forms"]):
            return redirect("edit meet entries", meet_pk=meet_pk, team_pk=team_pk)

    return render(
        request,
        "edit-meet-entries.html",
        {"meet_name": meet.name, "team_name": team.name, "sections": sections},
    )


@login_required
@require_http_methods(["GET"])
def view_meet_entries(request: HttpRequest, meet_pk: int, team_pk: int) -> HttpResponse:
    _validate_request(request.user, meet_pk, team_pk)
    return render(request, "view-meet-entries.html", {"sections": []})


def _validate_request(user: Profile, meet_pk: int, team_pk: int) -> None:
    if not Meet.objects.filter(pk=meet_pk).exists():
        raise Http404("Meet not found")
    if not Team.objects.filter(pk=team_pk).exists():
        raise Http404("Team not found")
    if not MeetTeamEntry.objects.filter(meet__pk=meet_pk, team__pk=team_pk).exists():
        raise Http404("Team not registered to meet")

    if user.is_superuser:
        return
    team_pks = CoachEntry.objects.filter(profile=user).values_list(
        "team__pk", flat=True
    )
    if team_pk not in team_pks:
        raise PermissionDenied("User is not registered to the team")
