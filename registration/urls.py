from django.urls import path

from . import views

urlpatterns = [
    path("athlete", views.manage_athletes, name="register athlete"),
    path(
        "meet/<int:meet_pk>/team/<int:team_pk>/",
        views.meet_entries_for_team,
        name="meet signup",
    ),
    # path(
    #     "meet/<int:meet_pk>/team/<int:team_pk>/save/",
    #     views.save_meet_entries_for_team,
    #     name="meet signup save",
    # ),
]
