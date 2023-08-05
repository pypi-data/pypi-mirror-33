from django.core.management.base import BaseCommand
from electionnight.celery import call_race_in_slack, call_race_on_twitter


class Command(BaseCommand):
    help = 'Sends a test call to Slack/Twitter bots'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        payload = {
            "race_id": '45897',
            "election_date": "06/30/18",
            "division": 'Texas',
            "division_slug": 'texas',
            "office": 'U.S. House, Texas, District 27',
            "candidate": 'Michael Cloud',
            "primary_party": None,
            "vote_percent": 0.557,
            "vote_count": 168162,
            "runoff": False,
            "precincts_reporting_percent": 0.80,
            "jungle": False,
            "runoff_election": False,
            "special_election": True
        }

        call_race_in_slack.delay(payload)
        call_race_on_twitter.delay(payload)
