from django.core.exceptions import ValidationError
from django.db import models
from common.models import BaseModel
from accounts.models import Profile


class League(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Gender(models.TextChoices):
    FEMALE = 'F', "Female"
    MALE = 'M', "Male"

    def __str__(self) -> str:
        return self.label


class Team(BaseModel):
    name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class Meet(BaseModel):
    start_date = models.DateField("start date")
    end_date = models.DateField("end date")
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.name} ({self.start_date})"

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("End date can not come before start date")


class Athlete(BaseModel):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    high_school_class_of = models.IntegerField(default=None, blank=True, null=True)

    @property
    def teams(self) -> str:
        team_ids = TeamAthleteEntry.objects.filter(athlete=self).values_list("team_id", flat=True)
        return " | ".join(
            team.name for team in Team.objects.filter(id__in=team_ids)
        )

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class LeagueTeamEntry(BaseModel):
    class Meta(BaseModel.Meta):
        verbose_name = "Team Entry"
        verbose_name_plural = "League Team Registry"

    league = models.ForeignKey(League, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.league} - {self.team}"


class MeetTeamEntry(BaseModel):
    class Meta(BaseModel.Meta):
        verbose_name = "Team Entry"
        verbose_name_plural = "Meet Team Registry"

    meet = models.ForeignKey(Meet, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.meet} - {self.team}"


class TeamAthleteEntry(BaseModel):
    class Meta(BaseModel.Meta):
        verbose_name = "Athlete Entry"
        verbose_name_plural = "Team Athlete Registry"

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.team} - {self.athlete}"


class Event(models.TextChoices):
    _200_YARD_MEDLEY_RELAY = "200 Yard Medley Relay"
    _200_YARD_FREESTYLE_RELAY = "200 Yard Freestyle Relay"
    _400_YARD_FREESTYLE_RELAY = "400 Yard Freestyle Relay"
    _200_YARD_INDIVIDUAL_MEDLEY = "200 Yard Individual Medley"
    _100_YARD_BUTTERFLY = "100 Yard Butterfly"
    _100_YARD_BACKSTROKE = "100 Yard Backstroke"
    _100_YARD_BREASTSTROKE = "100 Yard Breaststroke"
    _50_YARD_FREESTYLE = "50 Yard Freestyle"
    _100_YARD_FREESTYLE = "100 Yard Freestyle"
    _200_YARD_FREESTYLE = "200 Yard Freestyle"
    _500_YARD_FREESTYLE = "500 Yard Freestyle"


class MeetAthleteIndividualEntry(BaseModel):
    class Meta(BaseModel.Meta):
        verbose_name = "Individual Entry"
        verbose_name_plural = "Meet Individual Event Registry"

    meet = models.ForeignKey(Meet, on_delete=models.CASCADE)
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    event = models.CharField(max_length=30, choices=Event.choices)
    seed = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.meet} - {self.athlete} - {self.event} - {self.seed}"


class MeetAthleteRelayEntry(BaseModel):
    class Meta(BaseModel.Meta):
        verbose_name = "Relay Entry"
        verbose_name_plural = "Meet Relay Event Registry"

    meet = models.ForeignKey(Meet, on_delete=models.CASCADE)
    athlete_1 = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name="meetathleterelayregistry_set1")
    athlete_2 = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name="meetathleterelayregistry_set2")
    athlete_3 = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name="meetathleterelayregistry_set3")
    athlete_4 = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name="meetathleterelayregistry_set4")
    event = models.CharField(max_length=30, choices=Event.choices)
    seed = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

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
    class Meta(BaseModel.Meta):
        verbose_name = "Coach Entry"
        verbose_name_plural = "Coach Registry"

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.team} - {self.profile}"
