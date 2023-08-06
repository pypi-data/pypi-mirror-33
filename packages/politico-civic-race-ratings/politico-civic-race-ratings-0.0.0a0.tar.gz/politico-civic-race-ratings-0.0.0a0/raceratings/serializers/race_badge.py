from rest_framework import serializers

from raceratings.models import RaceBadge
from .badge_type import BadgeTypeSerializer


class RaceBadgeSerializer(serializers.ModelSerializer):
    badge_type = serializers.SerializerMethodField()

    def get_badge_type(self, obj):
        return BadgeTypeSerializer(obj.badge_type).data

    class Meta:
        model = RaceBadge
        fields = (
            'badge_type',
            'explanation',
        )
