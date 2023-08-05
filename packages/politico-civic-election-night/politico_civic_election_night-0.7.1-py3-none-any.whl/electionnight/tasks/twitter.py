import os
from argparse import Namespace
from urllib.parse import urlencode

import requests
import twitter
from celery import shared_task
from django.conf import settings
from electionnight.conf import settings as app_settings

CONSUMER_KEY = getattr(settings, 'CIVIC_TWITTER_CONSUMER_KEY', None)
CONSUMER_SECRET = getattr(settings, 'CIVIC_TWITTER_CONSUMER_SECRET', None)
ACCESS_TOKEN_KEY = getattr(settings, 'CIVIC_TWITTER_ACCESS_TOKEN_KEY', None)
ACCESS_TOKEN_SECRET = getattr(
    settings, 'CIVIC_TWITTER_ACCESS_TOKEN_SECRET', None)


def get_screenshot(division_slug, race_id):
    if app_settings.AWS_S3_BUCKET == 'interactives.politico.com':
        start_path = '/election-results'
        end_path = ''
    else:
        start_path = '/staging.interactives.politico.com/election-results'
        end_path = 'index.html'
    query = urlencode({
        'path': '{}/2018/{}/{}'.format(
            start_path,
            division_slug,
            end_path
        ),
        'selector': '.race-table-{}'.format(
            race_id
        ),
        'padding': '5px 0 0 10px'
    })
    root = 'http://politico-botshot.herokuapp.com/shoot/?'

    response = requests.get('{}{}'.format(root, query))

    folder = os.path.join(
        settings.BASE_DIR,
        'images'
    )

    if not os.path.exists(folder):
        os.makedirs(folder)

    with open('{}/{}.png'.format(folder, race_id), 'wb') as f:
        f.write(response.content)


def construct_status(
    party, candidate, office, runoff, division_slug, jungle, runoff_election
):
    party_labels = {
        'Democrat': 'Democratic',
        'Republican': 'Republican'
    }
    page_url = (
        'https://www.politico.com/election-results/2018'
        '/{}/'.format(division_slug)
    )
    if runoff_election:
        page_url += 'runoff'
    if party:
        if runoff:
            return (
                '🚨 NEW CALL: {} has advanced to a runoff'
                ' in the {} primary for {}. {}'
            ).format(
                candidate,
                party_labels[party],
                office,
                page_url
            )
        else:
            return '🚨 NEW CALL: {} has won the {} primary for {}. {}'.format(
                candidate,
                party_labels[party],
                office,
                page_url
            )
    elif jungle:
        return (
                '🚨 NEW CALL: {} has advanced to the general election'
                ' in the open primary for {}. {}'
            ).format(
                candidate,
                office,
                page_url
            )
    elif runoff_election:
        if party:
            return (
                '🚨 NEW CALL: {} has won the {}'
                ' primary runoff for {}. {}'
                ).format(
                candidate,
                party_labels[party],
                office,
                page_url
            )
    else:
        if runoff:
            return (
                '🚨 NEW CALL: {} has advanced to a runoff'
                ' in the race for {}. {}'
            ).format(
                candidate,
                office,
                page_url
            )
        else:
            return '🚨 NEW CALL: {} has won the race for {}. {}'.format(
                candidate,
                office,
                page_url
            )


@shared_task
def call_race_on_twitter(payload):
    payload = Namespace(**payload)

    get_screenshot(
        payload.division_slug,
        payload.race_id
    )

    status = construct_status(
        payload.primary_party,
        payload.candidate,
        payload.office,
        payload.runoff,
        payload.division_slug,
        payload.jungle,
        payload.runoff_election
    )

    api = twitter.Api(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token_key=ACCESS_TOKEN_KEY,
        access_token_secret=ACCESS_TOKEN_SECRET
    )

    with open('{}/images/{}.png'.format(
        settings.BASE_DIR, payload.race_id
    ), 'rb') as f:
        media_id = api.UploadMediaSimple(f)

    api.PostUpdate(
        status=status,
        media=[media_id]
    )
