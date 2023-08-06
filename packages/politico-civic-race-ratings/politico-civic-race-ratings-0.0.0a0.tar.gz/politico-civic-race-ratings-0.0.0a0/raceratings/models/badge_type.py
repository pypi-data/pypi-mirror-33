from django.db import models


class BadgeType(models.Model):
    """
    A risk factor contributing to a race rating
    """
    label = models.CharField(max_length=140)
    short_label = models.CharField(max_length=30)
    description = models.TextField()

    def __str__(self):
        return self.label
