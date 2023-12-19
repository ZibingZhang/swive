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
