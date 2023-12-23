from django.urls import path

from . import views

urlpatterns = [
    path("athlete", views.manage_athletes, name="register athlete"),
    path(
        "meet/<int:meet_pk>/team/<int:team_pk>/",
        views.meet_entry_form,
        name="meet signup",
    ),
    path(
        "meet/<int:meet_pk>/team/<int:team_pk>/save/",
        views.save_meet_entry_form,
        name="meet signup save",
    ),
]
