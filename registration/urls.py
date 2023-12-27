from django.urls import path

from . import views

urlpatterns = [
    path(
        "meet/<int:meet_pk>/team/<int:team_pk>/",
        views.meet_entries_for_team,
        name="meet entries",
    ),
]
