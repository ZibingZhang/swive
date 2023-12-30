from django.urls import path

from root import views

urlpatterns = [
    path("meets/all", views.all_meets, name="meets"),
    path("meet/<int:meet_pk>/teams", views.teams_for_meet, name="teams for meet"),
    path("teams/all", views.all_teams, name="all teams"),
    path("teams/mine", views.my_teams, name="my teams"),
    path("team/<int:team_pk>/meets", views.meets_for_team, name="teams for meet"),
]
