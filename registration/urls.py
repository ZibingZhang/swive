from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/meet/highschool/conference", views.signup_meet_highschool_conference, name="meet signup"),
    path("signup/meet/highschool/conference/save", views.signup_meet_highschool_conference_save, name="meet signup save"),
]
