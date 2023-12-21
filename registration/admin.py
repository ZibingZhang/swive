from django.contrib import admin
from common import utils
from common.admin import BaseAdmin
from registration.models import Meet, Team, Athlete, CoachEntry, LeagueTeamEntry, League, MeetTeamEntry, MeetAthleteIndividualEntry, MeetAthleteRelayEntry


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
    list_display = ("name", "start_date", "end_date", utils.linkify("league"))
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
    list_display = ("__str__", utils.linkify("team"))
    search_fields = ("first_name", "last_name", "team")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        teams_ids = CoachEntry.objects.filter(profile=request.user).values_list("team_id", flat=True)
        return qs.filter(team_id__in=teams_ids)


@admin.register(LeagueTeamEntry)
class LeagueTeamRegistryAdmin(BaseAdmin):
    list_display = ("id", utils.linkify("league"), utils.linkify("team"))


@admin.register(MeetTeamEntry)
class MeetTeamRegistryAdmin(BaseAdmin):
    list_display = ("id", utils.linkify("meet"), utils.linkify("team"))


@admin.register(MeetAthleteIndividualEntry)
class MeetAthleteIndividualRegistryAdmin(BaseAdmin):
    list_display = ("id", utils.linkify("meet"), utils.linkify("athlete"), "event", "seed")


@admin.register(MeetAthleteRelayEntry)
class MeetAthleteRelayRegistryAdmin(BaseAdmin):
    list_display = ("id", utils.linkify("meet"), utils.linkify("athlete_1"), utils.linkify("athlete_2"), utils.linkify("athlete_3"), utils.linkify("athlete_4"), "event", "seed")


@admin.register(CoachEntry)
class CoachRegistryAdmin(BaseAdmin):
    list_display = ("id", utils.linkify("team"), utils.linkify("profile"))
