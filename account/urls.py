from __future__ import annotations

from django.urls import path

from . import views

urlpatterns = [
    path("create", views.create_profile, name="create profile"),
    path("edit", views.edit_profile, name="edit profile"),
]
