import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from election.models import Race

from raceratings.managers import PageContentManager


class RatingPageContent(models.Model):
    """
    A specific page that content can attach to.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    allowed_types = models.Q(app_label='election', model='race') | \
        models.Q(app_label='raceratings', model='ratingpagetype')
    content_type = models.ForeignKey(
        ContentType,
        limit_choices_to=allowed_types,
        on_delete=models.CASCADE
    )
    object_id = models.CharField(max_length=500)
    content_object = GenericForeignKey('content_type', 'object_id')

    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='children',
        on_delete=models.PROTECT)

    objects = PageContentManager()

    def __str__(self):
        return self.content_label()

    def content_label(self):
        if self.content_type.model_class() == Race:
            return self.content_object.label
        else:
            if self.content_object.model_type == 'home':
                return 'Homepage'
            else:
                return 'Races'
