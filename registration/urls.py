from django.urls import path

from . import views

urlpatterns = [
    path(
        "entries/meet/<int:meet_pk>/team/<int:team_pk>/edit",
        views.edit_meet_entries,
        name="edit meet entries",
    ),
    path(
        "entries/meet/<int:meet_pk>/team/<int:team_pk>/view",
        views.view_meet_entries,
        name="view meet entries",
    ),
]
