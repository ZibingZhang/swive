from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin
from django.db import models
from import_export.admin import ImportExportModelAdmin

from common import utils
from common.forms import AthleteAdminForm
from common.models import Athlete, Meet, Team
from registration.models import CoachEntry, MeetTeamEntry

if TYPE_CHECKING:
    from django.http import HttpRequest


class BaseAdmin(ImportExportModelAdmin):
    pass


@admin.register(Team)
class TeamAdmin(BaseAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    def get_queryset(self, request: HttpRequest) -> models.QuerySet:
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(coachentry__profile=request.user)


@admin.register(Meet)
class MeetAdmin(BaseAdmin):
    list_display = ("name", "start_date", "end_date")
    list_filter = ("start_date", "end_date")
    search_fields = ("name", "start_date", "end_date")

    def get_queryset(self, request: HttpRequest) -> models.QuerySet:
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        teams_pks = CoachEntry.objects.filter(profile=request.user).values_list(
            "team__pk", flat=True
        )
        meet_pks = MeetTeamEntry.objects.filter(team_pk__in=teams_pks).values_list(
            "meet__pk", flat=True
        )
        return qs.filter(pk__in=meet_pks)


@admin.register(Athlete)
class AthleteAdmin(BaseAdmin):
    form = AthleteAdminForm
    list_display = (
        "__str__",
        utils.linkify_fk("team"),
        "active",
        "high_school_class_of",
    )
    list_filter = ("active",)
    search_fields = ("first_name", "last_name", "team__name", "high_school_class_of")

    def get_form(self, request, *args, **kwargs):
        form = super().get_form(request, *args, **kwargs)
        form.current_user = request.user
        return form

    def get_queryset(self, request: HttpRequest) -> models.QuerySet:
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        teams_pks = CoachEntry.objects.filter(profile=request.user).values_list(
            "team_id", flat=True
        )
        return qs.filter(team_id__in=teams_pks)
