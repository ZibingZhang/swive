from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from account.models import Profile
from common.models import Athlete, BaseModel, EventChoice, Meet, SoftDeleteModel, Team


class MeetEntry(SoftDeleteModel):
    meet = models.ForeignKey(Meet, on_delete=models.RESTRICT)
    team = models.ForeignKey(Team, on_delete=models.RESTRICT)
    event = models.CharField(max_length=30, choices=EventChoice.choices)
    order = models.PositiveIntegerField()
    seed = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    class Meta:
        abstract = True

    def clean(self) -> None:
        qs = type(self).objects.filter(
            meet=self.meet, team=self.team, event=self.event, order=self.order
        )
        if qs.exists() and qs.get() != self:
            raise ValidationError(f"Entry already exists")


class MeetIndividualEntry(MeetEntry):
    athlete = models.ForeignKey(Athlete, on_delete=models.RESTRICT)

    class Meta:
        verbose_name = "Individual Entry"
        verbose_name_plural = "Meet Individual Event Entries"
        constraints = [
            models.UniqueConstraint(
                fields=["meet", "team", "event", "order"],
                condition=Q(deleted=False),
                name="one MeetIndividualEntry per (meet, team, event, order)",
            )
        ]

    def __str__(self) -> str:
        return f"{self.meet} - {self.team} - {self.event} - {self.order} - {self.athlete} - {self.seed}"

    def clean(self) -> None:
        super().clean()


class MeetRelayEntry(MeetEntry):
    athlete_0 = models.ForeignKey(
        Athlete, on_delete=models.RESTRICT, related_name="meetrelayentry_set1"
    )
    athlete_1 = models.ForeignKey(
        Athlete, on_delete=models.RESTRICT, related_name="meetrelayentry_set2"
    )
    athlete_2 = models.ForeignKey(
        Athlete, on_delete=models.RESTRICT, related_name="meetrelayentry_set3"
    )
    athlete_3 = models.ForeignKey(
        Athlete, on_delete=models.RESTRICT, related_name="meetrelayentry_set4"
    )

    class Meta:
        verbose_name = "Relay Entry"
        verbose_name_plural = "Meet Relay Event Entries"
        constraints = [
            models.UniqueConstraint(
                fields=["meet", "team", "event", "order"],
                condition=Q(deleted=False),
                name="one MeetRelayEntry per (meet, team, event, order)",
            )
        ]

    @property
    def athletes(self) -> list[Athlete]:
        return [self.athlete_0, self.athlete_1, self.athlete_2, self.athlete_3]

    def clean(self) -> None:
        super().clean()
        athlete_ids = set()
        for athlete in self.athletes:
            if athlete.id in athlete_ids:
                raise ValidationError(f"Duplicate athlete {athlete}")
            athlete_ids.add(athlete.id)

    def __str__(self) -> str:
        return (
            f"{self.meet} - {self.team} - {self.event} - {self.order} - {self.athletes}"
        )


class CoachRequest(BaseModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="coach_requests"
    )

    class Meta:
        verbose_name = "Coach Request"
        verbose_name_plural = "Coach Requests"

    def __str__(self) -> str:
        return f"{self.team} - {self.profile}"
