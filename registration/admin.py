from django.contrib import admin
from django.utils.html import format_html

from common import utils
from common.admin import BaseAdmin
from registration.forms import CoachEntryForm
from registration.models import (
    CoachEntry,
    MeetIndividualEntry,
    MeetRelayEntry,
    MeetTeamEntry,
)


@admin.register(CoachEntry)
class CoachEntryAdmin(BaseAdmin):
    form = CoachEntryForm
    list_display = ("id", utils.linkify_fk("team"), utils.linkify_fk("profile"))


@admin.register(MeetTeamEntry)
class MeetTeamEntryAdmin(BaseAdmin):
    list_display = (
        "id",
        utils.linkify_fk("meet"),
        utils.linkify_fk("team"),
        lambda entry: format_html(
            '<a href="{}" target="_blank">Edit meet entries</a>',
            f"/registration/meet/{entry.meet.pk}/team/{entry.team.pk}",
        ),
    )
    list_filter = ("meet", "team")
    search_fields = ("meet", "team")


@admin.register(MeetIndividualEntry)
class MeetIndividualEntryAdmin(BaseAdmin):
    fields = (
        "meet",
        "team",
        "event",
        "order",
        "athlete",
        "seed",
    )
    list_display = (
        "id",
        utils.linkify_fk("meet"),
        utils.linkify_fk("team"),
        "event",
        "order",
        utils.linkify_fk("athlete"),
        "seed",
    )


@admin.register(MeetRelayEntry)
class MeetRelayEntryAdmin(BaseAdmin):
    fields = (
        "meet",
        "team",
        "event",
        "order",
        "athlete_0",
        "athlete_1",
        "athlete_2",
        "athlete_3",
        "seed",
    )
    list_display = (
        "id",
        utils.linkify_fk("meet"),
        utils.linkify_fk("team"),
        "event",
        "order",
        utils.linkify_fk("athlete_0"),
        utils.linkify_fk("athlete_1"),
        utils.linkify_fk("athlete_2"),
        utils.linkify_fk("athlete_3"),
        "seed",
    )
