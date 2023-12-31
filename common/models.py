from __future__ import annotations

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q

from common.constants import Event


class BaseModel(models.Model):
    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    def __init__(self, include_deleted: bool) -> None:
        super().__init__()
        self.include_deleted = include_deleted

    def get_queryset(self) -> models.QuerySet:
        if self.include_deleted:
            return super().get_queryset()
        else:
            return super().get_queryset().filter(deleted=False)


class SoftDeleteModel(BaseModel):
    deleted = models.BooleanField(default=False, editable=False)
    objects = SoftDeleteManager(include_deleted=False)
    all_objects = SoftDeleteManager(include_deleted=True)

    class Meta:
        abstract = True

    def delete(self, *args) -> None:
        """Mark the record as deleted instead of deleting it"""
        self.deleted = True
        self.save()


class Team(SoftDeleteModel):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Meet(SoftDeleteModel):
    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateField("start date", default=None, blank=True, null=True)
    end_date = models.DateField("end date", default=None, blank=True, null=True)
    entries_open = models.BooleanField(
        "entries open",
        default=False,
        help_text="Designates whether entries are open for editing for the meet.",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="Meet start date before end date",
                check=Q(start_date__lte=F("end_date")),
            )
        ]
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name}"


class Athlete(SoftDeleteModel):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    team = models.ForeignKey(Team, on_delete=models.RESTRICT)
    active = models.BooleanField(default=True)
    high_school_class_of = models.PositiveIntegerField(
        default=None,
        blank=True,
        null=True,
        validators=[MinValueValidator(1990), MaxValueValidator(2050)],
    )

    class Meta:
        ordering = ("team", "first_name", "last_name")

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.id})"


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
