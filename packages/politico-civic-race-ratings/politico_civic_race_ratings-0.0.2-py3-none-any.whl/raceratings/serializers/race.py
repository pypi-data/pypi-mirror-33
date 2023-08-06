from election.models import Race
from geography.models import DivisionLevel
from government.serializers import OfficeSerializer
from rest_framework import serializers
from rest_framework.reverse import reverse

from raceratings.models import RatingPageContent
from .race_rating import RaceRatingSerializer, RaceRatingAdminSerializer
from .race_badge import RaceBadgeSerializer


class RaceListSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse(
            'raceratings_api_race-detail',
            request=self.context['request'],
            kwargs={
                'pk': obj.pk
            })

    class Meta:
        model = Race
        fields = (
            'url',
            'uid',
            'label'
        )


class RaceSerializer(serializers.ModelSerializer):
    ratings = serializers.SerializerMethodField()
    badges = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    office = serializers.SerializerMethodField()

    def get_ratings(self, obj):
        return RaceRatingSerializer(obj.ratings, many=True).data

    def get_badges(self, obj):
        return RaceBadgeSerializer(obj.badges, many=True).data

    def get_content(self, obj):
        return RatingPageContent.objects.race_content(obj)

    def get_office(self, obj):
        return obj.office.label

    class Meta:
        model = Race
        fields = (
            'uid',
            'ratings',
            'badges',
            'content',
            'office',
        )


class RaceAdminSerializer(serializers.ModelSerializer):
    ratings = serializers.SerializerMethodField()
    badges = serializers.SerializerMethodField()
    office = serializers.SerializerMethodField()

    # a bunch of search fields
    abbrev = serializers.SerializerMethodField()

    def get_ratings(self, obj):
        return RaceRatingAdminSerializer(
            obj.ratings.order_by('created_date', 'pk'), many=True
        ).data

    def get_badges(self, obj):
        return RaceBadgeSerializer(obj.badges, many=True).data

    def get_office(self, obj):
        if obj.office.body and obj.office.body.slug == 'senate':
            label = '{} {}'.format(obj.office.division.label, 'Senate')
        else:
            label = obj.office.label

        if obj.special:
            return '{} Special'.format(label)
        else:
            return label

    def get_abbrev(self, obj):
        # for easier search
        if obj.office.division.level.slug == DivisionLevel.DISTRICT:
            postal = obj.office.division.parent.code_components['postal']
            code = int(obj.office.division.code)
            return '{}-{}'.format(postal, code)
        else:
            postal = obj.office.division.code_components['postal']

            if obj.office.body:
                return '{}-{}'.format(postal, obj.office.body.slug)
            else:
                return '{}-{}'.format(postal, 'governor')

    class Meta:
        model = Race
        fields = (
            'uid',
            'ratings',
            'badges',
            'office',
            'abbrev',
            'special'
        )
