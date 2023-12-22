from django.db import models
from common.constants import Event


class BaseManager(models.Manager):
    def get_queryset(self):
        return models.QuerySet(self.model, using=self._db).exclude(deleted=True)


class BaseModel(models.Model):
    class Meta:
        abstract = True

    deleted = models.BooleanField(default=False, editable=False)
    objects = BaseManager()

    def delete(self):
        """Mark the record as deleted instead of deleting it"""

        self.deleted = True
        self.save()


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
