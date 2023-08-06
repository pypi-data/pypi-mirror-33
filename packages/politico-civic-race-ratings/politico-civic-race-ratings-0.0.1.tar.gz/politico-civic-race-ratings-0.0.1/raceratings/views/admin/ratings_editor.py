from raceratings.conf import settings as app_settings
from raceratings.utils.auth import secure
from django.views.generic import TemplateView


@secure
class RatingsEditor(TemplateView):
    template_name = "raceratings/admin/ratings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['secret'] = app_settings.SECRET_KEY
        return context
