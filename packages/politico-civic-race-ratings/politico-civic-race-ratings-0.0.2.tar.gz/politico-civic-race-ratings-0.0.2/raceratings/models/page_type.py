import uuid

from django.db import models


class RatingPageType(models.Model):
    """
    A type of page that content can attach to.
    """
    RACE = 'Race'
    HOME = 'Home'

    ALLOWED_TYPES = (
        (RACE, 'race'),
        (HOME, 'home')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_type = models.CharField(max_length=4, choices=ALLOWED_TYPES)
