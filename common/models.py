from __future__ import annotations

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q

from common.constants import Event


class BaseManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return models.QuerySet(self.model, using=self._db).exclude(deleted=True)


class BaseModel(models.Model):
    deleted = models.BooleanField(default=False, editable=False)
    objects = BaseManager()

    class Meta:
        abstract = True

    def delete(self, *args) -> None:
        """Mark the record as deleted instead of deleting it"""
        self.deleted = True
        self.save()


class League(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Gender(models.TextChoices):
    FEMALE = "F", "Female"
    MALE = "M", "Male"

    def __str__(self) -> str:
        return self.label


class Team(BaseModel):
    name = models.CharField(max_length=50)
    gender = models.CharField(
        max_length=1, choices=Gender.choices, blank=True, null=True
    )

    def __str__(self) -> str:
        return self.name


class Meet(BaseModel):
    league = models.ForeignKey(League, on_delete=models.RESTRICT)
    start_date = models.DateField("start date")
    end_date = models.DateField("end date")
    name = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="start_date_before_end_date",
                check=Q(start_date__lte=F("end_date")),
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.start_date})"


class Athlete(BaseModel):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    team = models.ForeignKey(Team, on_delete=models.RESTRICT)
    high_school_class_of = models.PositiveIntegerField(
        default=None,
        blank=True,
        null=True,
        validators=[MinValueValidator(1990), MaxValueValidator(2050)],
    )

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.pk})"


class EventChoice(models.TextChoices):
    _1_METER_DIVING = Event.D_1_METER_DIVING
    _200_YARD_MEDLEY_RELAY = Event.S_200_YARD_MEDLEY_RELAY
    _200_YARD_FREESTYLE_RELAY = Event.S_200_YARD_FREESTYLE_RELAY
    _400_YARD_FREESTYLE_RELAY = Event.S_400_YARD_FREESTYLE_RELAY
    _200_YARD_INDIVIDUAL_MEDLEY = Event.S_200_YARD_INDIVIDUAL_MEDLEY
    _100_YARD_BUTTERFLY = Event.S_100_YARD_BUTTERFLY
    _100_YARD_BACKSTROKE = Event.S_100_YARD_BACKSTROKE
    _100_YARD_BREASTSTROKE = Event.S_100_YARD_BREASTSTROKE
    _50_YARD_FREESTYLE = Event.S_50_YARD_FREESTYLE
    _100_YARD_FREESTYLE = Event.S_100_YARD_FREESTYLE
    _200_YARD_FREESTYLE = Event.S_200_YARD_FREESTYLE
    _500_YARD_FREESTYLE = Event.S_500_YARD_FREESTYLE
