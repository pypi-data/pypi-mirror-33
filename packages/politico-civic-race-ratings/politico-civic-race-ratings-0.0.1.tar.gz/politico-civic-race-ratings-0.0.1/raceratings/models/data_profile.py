from django.contrib.postgres.fields import JSONField
from django.db import models
from geography.models import Division


class DataProfile(models.Model):
    """
    A data profile of a division
    """
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    data = JSONField()

    def __str__(self):
        return '{} profile'.format(self.division.label)
