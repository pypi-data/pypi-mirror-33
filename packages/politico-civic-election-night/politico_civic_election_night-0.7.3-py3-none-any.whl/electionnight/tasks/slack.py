import time
from argparse import Namespace
from datetime import datetime

from celery import shared_task
from django.conf import settings
from electionnight.conf import settings as app_settings
from slacker import Slacker

SLACK_TOKEN = getattr(settings, 'CIVIC_SLACK_TOKEN', None)


def get_client():
    if SLACK_TOKEN:
        return Slacker(SLACK_TOKEN)
    return None


@shared_task
def call_race_in_slack(payload):
    payload = Namespace(**payload)

    state_path = payload.division_slug
    if payload.runoff_election:
        state_path = '{}/runoff'.format(state_path)

    if payload.special_election:
        parsed = datetime.strptime(payload.election_date, '%m/%d/%y')
        month = parsed.strftime('%b')
        day = parsed.strftime('%d')
        state_path = '{}/special-election/{}-{}'.format(
            state_path,
            month.lower(),
            day
        )

    if app_settings.AWS_S3_BUCKET == 'interactives.politico.com':
        start_path = 'https://www.politico.com/election-results/2018'
        end_path = ''
    else:
        start_path = 'https://s3.amazonaws.com/staging.interactives.politico.com/election-results/2018' # noqa
        end_path = 'index.html'

    page_path = '{}/{}/{}'.format(start_path, state_path, end_path)

    if payload.runoff:
        WINNING = '✓ *{}* will advance to a runoff.'.format(payload.candidate)
    else:
        WINNING = '✓ *{}* declared winner.'.format(payload.candidate)

    attachment_data = [{
        'fallback': '🚨 Race called in *{}*'.format(payload.division.upper()),
        'color': '#6DA9CC',
        "pretext": '<!here|here> :rotating_light: Race called in *{}*'.format(
            payload.division.upper()
        ),
        'mrkdwn_in': ['fields'],
        "author_name": "Election Bot",
        "author_icon": "https://pbs.twimg.com/profile_images/998954486205898753/gbb2psb__400x400.jpg",  # noqa
        "title": payload.office,
        "title_link": page_path,
        "text": WINNING,
        "footer": "Associated Press",
        "fields": [
            {
                "title": "Winning vote",
                "value": "{}% | {:,} votes".format(
                    int(round(payload.vote_percent * 100)),
                    int(payload.vote_count)
                ),
                "short": True
            },
            {
                "title": "Precincts reporting",
                "value": "{}%".format(
                    int(round(payload.precincts_reporting_percent * 100))
                ),
                "short": True
            }
        ],
        'ts': int(time.time())
    }]

    client = get_client()

    if app_settings.AWS_S3_BUCKET == 'interactives.politico.com':
        channel = '#elections-bot'
    else:
        channel = '#elections-bot-stg'

    client.chat.post_message(
        channel,
        '',
        attachments=attachment_data,
        as_user=False,
        username='Elections Bot'
    )
