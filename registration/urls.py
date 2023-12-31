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
]
