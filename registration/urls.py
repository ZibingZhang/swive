from django.urls import path

from . import views

urlpatterns = [
    path(
        "entries/meet/<int:meet_id>/team/<int:team_id>/edit",
        views.edit_meet_entries,
        name="edit meet entries",
    ),
    path(
        "entries/meet/<int:meet_id>/team/<int:team_id>/view",
        views.view_meet_entries,
        name="view meet entries",
    ),
    path(
        "teams/join",
        views.team_coach_status,
        name="team coach status",
    ),
    path(
        "teams/join/requests",
        views.coach_requests,
        name="coach requests",
    ),
]
