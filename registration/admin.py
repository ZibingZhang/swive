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
    search_fields = (
        "team__name",
        "profile__first_name",
        "profile__last_name",
        "profile__username",
    )


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
    search_fields = ("meet__name", "team__name")


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
    search_fields = (
        "meet__name",
        "team__name",
        "event",
        "athlete__first_name",
        "athlete__last_name",
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
    search_fields = (
        "meet__name",
        "team__name",
        "event",
        "athlete_0__first_name",
        "athlete_0__last_name",
        "athlete_1__first_name",
        "athlete_1__last_name",
        "athlete_2__first_name",
        "athlete_2__last_name",
        "athlete_3__first_name",
        "athlete_3__last_name",
        "seed",
    )
