from election.models import Race
from rest_framework.views import APIView
from rest_framework.response import Response

from raceratings.models import RatingPageContent
from raceratings.serializers import RaceSerializer


class HomeView(APIView):
    def get(self, request, format=None):
        races = Race.objects.filter(
            cycle__slug='2018', special=False
        ).order_by('office__division__label')
        race_data = RaceSerializer(races, many=True).data

        content = RatingPageContent.objects.home_content()

        context = {
            'races': race_data,
            'content': content
        }

        return Response(context)
