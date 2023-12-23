from django.core.exceptions import ValidationError
from django.db import models

from accounts.models import Profile
from common.models import Athlete, BaseModel, EventChoice, League, Meet, Team


class LeagueTeamEntry(BaseModel):
    league = models.ForeignKey(League, on_delete=models.RESTRICT)
    team = models.ForeignKey(Team, on_delete=models.RESTRICT)

    class Meta(BaseModel.Meta):
        verbose_name = "League Team Entry"
        verbose_name_plural = "League Team Entries"

    def __str__(self) -> str:
        return f"{self.league} - {self.team}"


class MeetTeamEntry(BaseModel):
    meet = models.ForeignKey(Meet, on_delete=models.RESTRICT)
    team = models.ForeignKey(Team, on_delete=models.RESTRICT)

    class Meta(BaseModel.Meta):
        verbose_name = "Meet Team Entry"
        verbose_name_plural = "Meet Team Entries"

    def __str__(self) -> str:
        return f"{self.meet} - {self.team}"

    @property
    def edit(self) -> str:
        return "Edit meet entries"


class MeetAthleteIndividualEntry(BaseModel):
    meet = models.ForeignKey(Meet, on_delete=models.RESTRICT)
    athlete = models.ForeignKey(Athlete, on_delete=models.RESTRICT)
    event = models.CharField(max_length=30, choices=EventChoice.choices)
    seed = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name = "Individual Entry"
        verbose_name_plural = "Meet Individual Event Entries"

    def __str__(self) -> str:
        return f"{self.meet} - {self.athlete} - {self.event} - {self.seed}"


class MeetAthleteRelayEntry(BaseModel):
    meet = models.ForeignKey(Meet, on_delete=models.RESTRICT)
    athlete_1 = models.ForeignKey(
        Athlete, on_delete=models.RESTRICT, related_name="meetathleterelayregistry_set1"
    )
    athlete_2 = models.ForeignKey(
        Athlete, on_delete=models.RESTRICT, related_name="meetathleterelayregistry_set2"
    )
    athlete_3 = models.ForeignKey(
        Athlete, on_delete=models.RESTRICT, related_name="meetathleterelayregistry_set3"
    )
    athlete_4 = models.ForeignKey(
        Athlete, on_delete=models.RESTRICT, related_name="meetathleterelayregistry_set4"
    )
    event = models.CharField(max_length=30, choices=EventChoice.choices)
    seed = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name = "Relay Entry"
        verbose_name_plural = "Meet Relay Event Entries"

    @property
    def athletes(self) -> list[Athlete]:
        return [self.athlete_1, self.athlete_2, self.athlete_3, self.athlete_4]

    def clean(self) -> None:
        athlete_pks = set()
        for athlete in self.athletes:
            if athlete.pk in athlete_pks:
                raise ValidationError(f"Duplicate athlete {athlete}")
            athlete_pks.add(athlete.pk)

    def __str__(self) -> str:
        return f"{self.meet} - {self.athletes} - {self.event} - {self.seed}"


class CoachEntry(BaseModel):
    team = models.ForeignKey(Team, on_delete=models.RESTRICT)
    profile = models.ForeignKey(Profile, on_delete=models.RESTRICT)

    class Meta(BaseModel.Meta):
        verbose_name = "Coach Entry"
        verbose_name_plural = "Coach Entries"

    def __str__(self) -> str:
        return f"{self.team} - {self.profile}"
