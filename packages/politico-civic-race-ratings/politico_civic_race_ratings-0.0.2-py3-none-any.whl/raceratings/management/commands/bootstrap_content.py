from django.core.management.base import BaseCommand
from election.models import Race
from tqdm import tqdm

from .methods import BootstrapContentMethods


class Command(BaseCommand, BootstrapContentMethods):
    help = (
        'Bootstraps page content items for pages for all elections on an '
        'election day. Must be run AFTER bootstrap_election command.'
    )

    def handle(self, *args, **options):
        print('Bootstrapping page content')
        self.bootstrap_homepage_content()
        for race in tqdm(Race.objects.filter(special=False)):
            self.bootstrap_race_content(race)
        print('Done.')
