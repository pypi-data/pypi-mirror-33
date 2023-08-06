from django.contrib.auth.models import User
from django.db import models


class Author(models.Model):
    """
    An author.
    """
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    user = models.OneToOneField(
        User,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='rating_author'
    )

    def __str__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)
