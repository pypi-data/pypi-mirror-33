from django.core.management.base import BaseCommand
from electionnight.celery import call_race_in_slack, call_race_on_twitter


class Command(BaseCommand):
    help = 'Sends a test call to Slack/Twitter bots'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        payload = {
            "race_id": '45897',
            "division": 'Texas',
            "division_slug": 'texas',
            "office": 'the House seat in Texas’ 27th District',
            "candidate": 'Roy Barrera',
            "primary_party": None,
            "vote_percent": 0.18,
            "vote_count": 36987,
            "runoff": True,
            "precincts_reporting_percent": 1,
            "jungle": False,
            "runoff_election": False,
            "special_election": True,
            "page_url": 'https://s3.amazonaws.com/staging.interactives.politico.com/election-results/2018/texas/special-election/jun-30/index.html' # noqa
        }

        call_race_in_slack.delay(payload)
        call_race_on_twitter.delay(payload)
