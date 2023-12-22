from django.urls import path

from . import views

urlpatterns = [
    path("athlete", views.manage_athletes, name="register athlete"),
    path(
        "meet/<int:meet_id>/team/<int:team_id>/",
        views.meet_entry_form,
        name="meet signup",
    ),
    path(
        "meet/<int:meet_id>/team/<int:team_id>/save/",
        views.save_meet_entry_form,
        name="meet signup save",
    ),
]
