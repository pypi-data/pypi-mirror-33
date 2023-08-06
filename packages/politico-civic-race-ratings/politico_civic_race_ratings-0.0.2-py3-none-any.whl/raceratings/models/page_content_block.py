import uuid

from django.db import models

from raceratings.fields import MarkdownField


class RatingPageContentBlock(models.Model):
    """
    A block of content for an individual page.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(
        'RatingPageContent', related_name='blocks', on_delete=models.PROTECT)
    content_type = models.ForeignKey(
        'RatingPageContentType', related_name='+', on_delete=models.PROTECT)
    content = MarkdownField()

    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        unique_together = ('page', 'content_type',)

    def __str__(self):
        return self.content_type.name
