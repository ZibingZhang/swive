from django.contrib import admin
from django.utils.html import format_html

from common import utils
from common.admin import BaseAdmin
from registration.models import (
    CoachEntry,
    LeagueTeamEntry,
    MeetIndividualEntry,
    MeetRelayEntry,
    MeetTeamEntry,
)


@admin.register(LeagueTeamEntry)
class LeagueTeamRegistryAdmin(BaseAdmin):
    list_display = ("id", utils.linkify_fk("league"), utils.linkify_fk("team"))


@admin.register(MeetTeamEntry)
class MeetTeamRegistryAdmin(BaseAdmin):
    list_display = (
        "id",
        utils.linkify_fk("meet"),
        utils.linkify_fk("team"),
        lambda entry: format_html(
            '<a href="{}" target="_blank">Edit meet entries</a>',
            f"/registration/meet/{entry.meet.pk}/team/{entry.team.pk}",
        ),
    )


@admin.register(MeetIndividualEntry)
class MeetIndividualRegistryAdmin(BaseAdmin):
    fields = ("meet", "athlete", "event", "seed")
    list_display = (
        "id",
        utils.linkify_fk("meet"),
        utils.linkify_fk("athlete"),
        "event",
        "seed",
    )


@admin.register(MeetRelayEntry)
class MeetRelayRegistryAdmin(BaseAdmin):
    fields = (
        "meet",
        "athlete_1",
        "athlete_2",
        "athlete_3",
        "athlete_4",
        "event",
        "seed",
    )
    list_display = (
        "id",
        utils.linkify_fk("meet"),
        utils.linkify_fk("athlete_1"),
        utils.linkify_fk("athlete_2"),
        utils.linkify_fk("athlete_3"),
        utils.linkify_fk("athlete_4"),
        "event",
        "seed",
    )


@admin.register(CoachEntry)
class CoachRegistryAdmin(BaseAdmin):
    list_display = ("id", utils.linkify_fk("team"), utils.linkify_fk("profile"))
