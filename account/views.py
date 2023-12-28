from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from account.forms import ProfileChangeForm, ProfileCreationForm

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


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
def edit_profile(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return render(request, "edit.html")

    context = {
        "profile_change_form": ProfileChangeForm(instance=request.user),
        "password_change_form": PasswordChangeForm(request.user),
    }
    if request.method == "POST":
        if "first_name" in request.POST:
            form = ProfileChangeForm(request.POST, instance=request.user)
            context["profile_change_form"] = form
            if form.is_valid():
                form.save()
        else:
            form = PasswordChangeForm(request.user, request.POST)
            context["password_change_form"] = form
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                return redirect("edit profile")
    return render(request, "edit.html", context)
