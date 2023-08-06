from django.contrib.postgres.fields import JSONField
from django.db import models
from election.models import Race
from raceratings.fields import MarkdownField

from .author import Author
from .category import Category


class RaceRating(models.Model):
    """
    An individual rating for a race
    """
    created_date = models.DateField(auto_now_add=True)
    author = models.ForeignKey(
        Author, on_delete=models.PROTECT, related_name='ratings'
    )
    race = models.ForeignKey(
        Race, on_delete=models.CASCADE, related_name='ratings'
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='ratings'
    )
    explanation = MarkdownField(blank=True, null=True)
    incumbent = models.BooleanField(default=False)

    def __str__(self):
        return '{0}: {1}'.format(self.race.label, self.category.short_label)
