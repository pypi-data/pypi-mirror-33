from django.core.management.base import BaseCommand
from electionnight.celery import call_race_in_slack, call_race_on_twitter


class Command(BaseCommand):
    help = 'Sends a test call to Slack/Twitter bots'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        payload = {
            "race_id": '1394',
            "division": 'Alabama',
            "division_slug": 'alabama',
            "office": 'Alabama U.S. House District 1',
            "candidate": 'Robert Kennedy',
            "primary_party": 'Democrat',
            "vote_percent": 0.515234,
            "vote_count": 35671,
            "runoff": False,
            "precincts_reporting_percent": 0.88234,
            "jungle": False,
            "runoff_election": False
        }

        call_race_in_slack.delay(payload)
        call_race_on_twitter.delay(payload)
