from django.contrib import admin
from common import utils
from common.admin import BaseAdmin
from registration.models import Meet, Team, Athlete, CoachEntry, LeagueTeamEntry, League, MeetTeamEntry, MeetAthleteIndividualEntry, MeetAthleteRelayEntry
from django.utils.html import format_html


@admin.register(League)
class LeagueAdmin(BaseAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Team)
class TeamAdmin(BaseAdmin):
    list_display = ("name", "gender")
    list_filter = ("gender",)
    search_fields = ("name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(coachregistry__profile=request.user)


@admin.register(Meet)
class MeetAdmin(BaseAdmin):
    list_display = ("name", "start_date", "end_date", utils.linkify_fk("league"))
    list_filter = ("name", "start_date", "end_date")
    search_fields = ("name", "start_date", "end_date")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        teams_ids = CoachEntry.objects.filter(profile=request.user).values_list("team_id", flat=True)
        meet_ids = MeetTeamEntry.objects.filter(team_id__in=teams_ids).values_list("meet_id", flat=True)
        return qs.filter(id__in=meet_ids)


@admin.register(Athlete)
class AthleteAdmin(BaseAdmin):
    list_display = ("__str__", utils.linkify_fk("team"))
    search_fields = ("first_name", "last_name", "team")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        teams_ids = CoachEntry.objects.filter(profile=request.user).values_list("team_id", flat=True)
        return qs.filter(team_id__in=teams_ids)


@admin.register(LeagueTeamEntry)
class LeagueTeamRegistryAdmin(BaseAdmin):
    list_display = ("id", utils.linkify_fk("league"), utils.linkify_fk("team"))


@admin.register(MeetTeamEntry)
class MeetTeamRegistryAdmin(BaseAdmin):
    list_display = ("id", utils.linkify_fk("meet"), utils.linkify_fk("team"), lambda entry: format_html('<a href="{}">Edit meet entries</a>', f"/registration/meet/{entry.meet_id}/team/{entry.team_id}"))


@admin.register(MeetAthleteIndividualEntry)
class MeetAthleteIndividualRegistryAdmin(BaseAdmin):
    list_display = ("id", utils.linkify_fk("meet"), utils.linkify_fk("athlete"), "event", "seed")


@admin.register(MeetAthleteRelayEntry)
class MeetAthleteRelayRegistryAdmin(BaseAdmin):
    list_display = ("id", utils.linkify_fk("meet"), utils.linkify_fk("athlete_1"), utils.linkify_fk("athlete_2"),
                    utils.linkify_fk("athlete_3"), utils.linkify_fk("athlete_4"), "event", "seed")


@admin.register(CoachEntry)
class CoachRegistryAdmin(BaseAdmin):
    list_display = ("id", utils.linkify_fk("team"), utils.linkify_fk("profile"))
