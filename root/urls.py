from django.urls import path

from root import views

urlpatterns = [
    path("meets/all", views.all_meets, name="meets"),
    path("meet/<int:meet_pk>/teams", views.teams_for_meet, name="teams for meet"),
    path("teams/all", views.all_teams, name="teams"),
]
