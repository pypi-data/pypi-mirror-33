from django.conf.urls import include, url
from django.urls import path, re_path

from .views import Home, RatingsEditor
from .viewsets import HomeView, RaceViewSet, RaceList, RatingAdminView


urlpatterns = [
    path('', Home.as_view(), name='raceratings-home'),
    path('ratings/edit', RatingsEditor.as_view(), name='raceratings-editor'),
    re_path(
        r'^api/home/$',
        HomeView.as_view(),
        name='raceratings_api_home'
    ),
    re_path(
        r'^api/races/$',
        RaceList.as_view(),
        name='raceratings_api_race-list'
    ),
    re_path(
        r'^api/races/(?P<pk>.+)/$',
        RaceViewSet.as_view(),
        name='raceratings_api_race-detail'
    ),
    re_path(
        r'^api/admin/ratings/$',
        RatingAdminView.as_view(),
        name='raceratings_api_ratings-admin'
    ),
]
