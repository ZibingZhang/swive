from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("athlete", views.athlete, name="register athlete"),
    path("meet/<int:meet_id>/team/<int:team_id>/", views.meet_entry, name="meet signup"),
    path("conference/save/", views.signup_meet_highschool_conference_save, name="meet signup save"),
]
