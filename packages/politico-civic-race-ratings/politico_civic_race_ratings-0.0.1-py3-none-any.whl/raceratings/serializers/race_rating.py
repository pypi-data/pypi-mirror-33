from rest_framework import serializers

from raceratings.models import RaceRating
from .author import AuthorSerializer
from .category import CategorySerializer


class RaceRatingSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    def get_author(self, obj):
        return AuthorSerializer(obj.author).data

    def get_category(self, obj):
        return CategorySerializer(obj.category).data

    class Meta:
        model = RaceRating
        fields = (
            'created_date',
            'author',
            'category',
            'explanation',
            'incumbent'
        )


class RaceRatingAdminSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        return obj.category.short_label

    class Meta:
        model = RaceRating
        fields = (
            'pk',
            'created_date',
            'rating',
            'explanation',
            'incumbent'
        )
