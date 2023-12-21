from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from registration.models import Athlete
from common.models import INDIVIDUAL_EVENTS
from registration.forms import MeetAthleteRelayEntryForm, MeetAthleteIndividualEntryForm, AthleteForm


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@login_required
def meet_entry_form(request, meet_id, team_id):
    if request.method == "GET":
        sections = []
        for event in INDIVIDUAL_EVENTS:
            sections.append({
                "event": event.label,
                "forms": [
                    MeetAthleteIndividualEntryForm(prefix=f"{event}_{i}_") for i in range(4)
                ]
            })
        return render(request, "conference.html", {"sections": sections})


@login_required
def save_meet_entry_form(request, meet_id, team_id):
    if request.method == "POST":
        print(request._post)
        return HttpResponse(200)


@login_required
def athlete(request):
    if request.method == "GET":
        return render(request, "athletes.html", {"form": AthleteForm(), "athletes": Athlete.objects.filter()})
