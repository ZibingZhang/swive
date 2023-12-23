from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin
from django.db import models
from import_export.admin import ImportExportModelAdmin

from common import utils
from common.models import Athlete, League, Meet, Team
from registration.models import CoachEntry, MeetTeamEntry

if TYPE_CHECKING:
    from django.http import HttpRequest


class BaseAdmin(ImportExportModelAdmin):
    pass


@admin.register(League)
class LeagueAdmin(BaseAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Team)
class TeamAdmin(BaseAdmin):
    list_display = ("name", "gender")
    list_filter = ("gender",)
    search_fields = ("name",)

    def get_queryset(self, request: HttpRequest) -> models.QuerySet:
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(coachentry__profile=request.user)


@admin.register(Meet)
class MeetAdmin(BaseAdmin):
    list_display = ("name", "start_date", "end_date", utils.linkify_fk("league"))
    list_filter = ("name", "start_date", "end_date")
    search_fields = ("name", "start_date", "end_date")

    def get_queryset(self, request: HttpRequest) -> models.QuerySet:
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        teams_ids = CoachEntry.objects.filter(profile=request.user).values_list(
            "team_id", flat=True
        )
        meet_ids = MeetTeamEntry.objects.filter(team_id__in=teams_ids).values_list(
            "meet_id", flat=True
        )
        return qs.filter(id__in=meet_ids)


@admin.register(Athlete)
class AthleteAdmin(BaseAdmin):
    list_display = ("__str__", utils.linkify_fk("team"))
    search_fields = ("first_name", "last_name", "team")

    def get_queryset(self, request: HttpRequest) -> models.QuerySet:
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        teams_ids = CoachEntry.objects.filter(profile=request.user).values_list(
            "team_id", flat=True
        )
        return qs.filter(team_id__in=teams_ids)
