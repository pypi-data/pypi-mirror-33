from election.models import Race
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from raceratings.models import Author, Category, RaceRating
from raceratings.serializers import RaceAdminSerializer


class RatingAdminView(APIView):
    def get(self, request, format=None):
        races = Race.objects.filter(
            cycle__slug='2018', special=False
        ).order_by('office__division__label')

        minnesota = Race.objects.filter(
            cycle__slug='2018',
            special=True,
            office__division__label='Minnesota',
            office__body__slug='senate'
        )

        mississippi = Race.objects.filter(
            cycle__slug='2018',
            special=True,
            office__division__label='Mississippi',
            office__body__slug='senate'
        )

        races = races | minnesota | mississippi

        race_data = RaceAdminSerializer(races, many=True).data

        return Response(race_data)

    def post(self, request, format=None):
        steve = Author.objects.get(first_name='Steve', last_name='Shepard')

        for uid, ratings in request.data.items():
            race = Race.objects.get(uid=uid)
            last_rating = race.ratings.latest('created_date')
            for pk, data in ratings.items():
                category = None
                expl = None

                if data.get('category'):
                    category = Category.objects.get(
                        short_label=data['category']
                    )

                if data.get('explanation'):
                    expl = data['explanation']

                if data['post_type'] == 'create':
                    # can't have a new rating without a category
                    if not category:
                        continue

                    # if a new rating came through with the same rating,
                    # ignore it
                    if category == last_rating.category:
                        continue

                    RaceRating.objects.create(
                        race=race,
                        author=steve,
                        category=category,
                        explanation=expl
                    )
                elif data['post_type'] == 'update':
                    rating = RaceRating.objects.get(pk=pk)

                    rating.category = category if category else rating.category
                    rating.explanation = expl if expl else rating.explanation

                    rating.save()

        return Response('created ratings', status=status.HTTP_201_CREATED)
