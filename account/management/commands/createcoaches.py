from __future__ import annotations

import argparse
import re

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db.models import Count

from common.models import Coach, Team


class Command(BaseCommand):
    help = "Create coaches for teams without a coach"

    def add_arguments(self, parser):
        parser.add_argument("--execute", action=argparse.BooleanOptionalAction)

    def handle(self, *args, **options):
        execute = options["execute"]

        print("username,password")
        for team in Team.objects.all().annotate(Count("coaches")):
            username = re.sub(r"\W", "", team.name).lower()
            password = username + "password"
            print(f"{username},{password}")

            if execute and team.coaches__count == 0:
                profile = get_user_model().objects.create_user(
                    username=username, password=password
                )
                Coach.objects.create(profile=profile, team=team)
