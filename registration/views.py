from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from registration.models import Athlete
from registration.forms import MeetAthleteRelayEntryForm, MeetAthleteIndividualEntryForm, AthleteForm


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@login_required
def signup_meet_highschool_conference(request):
    if request.method == "GET":
        return render(request, "conference.html", {"form": MeetAthleteIndividualEntryForm()})


@login_required
def signup_meet_highschool_conference_save(request):
    if request.method == "POST":
        print(request._post)
        return HttpResponse(200)


@login_required
def athlete(request):
    if request.method == "GET":
        return render(request, "athletes.html", {"form": AthleteForm(), "athletes": Athlete.objects.filter(id=1)})
