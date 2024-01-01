from django.contrib import admin

from common import utils
from common.admin import BaseAdmin
from registration.models import CoachRequest, MeetIndividualEntry, MeetRelayEntry


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


@admin.register(CoachRequest)
class CoachRequestAdmin(BaseAdmin):
    pass
