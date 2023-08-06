from django.contrib import admin

from raceratings.models import (Author, BadgeType, Category, DataProfile,
                                PageContent, RaceRating, RaceBadge)

from .page_content import PageContentAdmin
from .race_badge import RaceBadgeAdmin
from .race_rating import RaceRatingAdmin

admin.site.register(Author)
admin.site.register(BadgeType)
admin.site.register(Category)
admin.site.register(DataProfile)
admin.site.register(PageContent, PageContentAdmin)
admin.site.register(RaceRating, RaceRatingAdmin)
admin.site.register(RaceBadge, RaceBadgeAdmin)
