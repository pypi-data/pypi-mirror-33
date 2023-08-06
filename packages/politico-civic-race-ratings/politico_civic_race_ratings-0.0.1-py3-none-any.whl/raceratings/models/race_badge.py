from django.contrib.postgres.fields import JSONField
from django.db import models

from election.models import Race
from raceratings.fields import MarkdownField

from .badge_type import BadgeType


class RaceBadge(models.Model):
    """
    A risk factor contributing to a race rating
    """
    badge_type = models.ForeignKey(BadgeType, on_delete=models.PROTECT)
    explanation = MarkdownField(blank=True, null=True)
    race = models.ForeignKey(
        Race, on_delete=models.CASCADE, related_name='badges'
    )
