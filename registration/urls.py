from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("athlete", views.athlete, name="register athlete"),
    path("meet/<int:meet_id>/team/<int:team_id>/", views.meet_entry_form, name="meet signup"),
    path("meet/<int:meet_id>/team/<int:team_id>/save/", views.save_meet_entry_form, name="meet signup save"),
]
