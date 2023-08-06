from raceratings.models import BadgeType
from rest_framework import serializers


class BadgeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BadgeType
        fields = (
            'label',
            'short_label',
            'description'
        )
