from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from common import utils
from common.forms import AthleteAdminForm
from common.models import Athlete, Coach, Meet, MeetTeam, Team

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
        return request.user.teams.all()


@admin.register(Meet)
class MeetAdmin(BaseAdmin):
    list_display = ("name", "start_date", "end_date", "entries_open")
    list_filter = ("start_date", "end_date")
    search_fields = ("name", "start_date", "end_date")

    def get_queryset(self, request: HttpRequest) -> models.QuerySet:
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        teams = request.user.teams.all()
        meet_ids = MeetTeam.objects.filter(team__in=teams).values_list(
            "meet", flat=True
        )
        return Meet.objects.filter(id__in=meet_ids)


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
        return qs.filter(team__in=request.user.teams.all())


@admin.register(Coach)
class CoachAdmin(BaseAdmin):
    list_display = ("id", utils.linkify_fk("team"), utils.linkify_fk("profile"))
    search_fields = (
        "team__name",
        "profile__first_name",
        "profile__last_name",
        "profile__username",
    )


@admin.register(MeetTeam)
class MeetTeamAdmin(BaseAdmin):
    list_display = (
        "id",
        utils.linkify_fk("meet"),
        utils.linkify_fk("team"),
        lambda entry: format_html(
            '<a href="{}" target="_blank">Edit meet entries</a>',
            f"/registration/entries/meet/{entry.meet.id}/team/{entry.team.id}/edit",
        ),
    )
    search_fields = ("meet__name", "team__name")
