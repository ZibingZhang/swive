from django.db import models


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


class Event(models.TextChoices):
    _1_METER_DIVING = "1 Meter Diving"
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


INDIVIDUAL_EVENTS = [
    Event._200_YARD_FREESTYLE,
    Event._200_YARD_INDIVIDUAL_MEDLEY,
    Event._50_YARD_FREESTYLE,
    Event._100_YARD_BUTTERFLY,
    Event._100_YARD_FREESTYLE,
    Event._500_YARD_FREESTYLE,
    Event._100_YARD_BACKSTROKE,
    Event._100_YARD_BREASTSTROKE,
]
