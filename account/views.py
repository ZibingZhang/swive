from django.contrib.auth import login
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from account.forms import ProfileChangeForm, ProfileCreationForm


@require_http_methods(["GET", "POST"])
def create_profile(request) -> HttpResponse:
    if request.method == "GET":
        form = ProfileCreationForm()
    elif request.method == "POST":
        form = ProfileCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    return render(request, "create.html", {"form": form})


@require_http_methods(["GET", "POST"])
def edit_profile(request) -> HttpResponse:
    if request.method == "GET":
        form = ProfileChangeForm(instance=request.user)
    elif request.method == "POST":
        form = ProfileChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
    return render(request, "edit.html", {"form": form})
