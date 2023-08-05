import json
import subprocess
import sys
from time import sleep

from tqdm import tqdm

from django.core.exceptions import ObjectDoesNotExist
from django.core.management import call_command
from django.core.management.base import BaseCommand
from election.models import Candidate, CandidateElection
from electionnight.celery import call_race_in_slack, call_race_on_twitter
from electionnight.conf import settings as app_settings
from electionnight.models import APElectionMeta
from geography.models import Division, DivisionLevel
from vote.models import Votes


class Command(BaseCommand):
    help = (
        'Ingests master results JSON file from Elex and updates the results '
        'models in Django.'
    )

    def download_results(self, options):
        writefile = open('master.json', 'w')
        elex_args = [
            'elex',
            'results',
            options['election_date'],
            '--national-only',
            '-o',
            'json',
        ]

        if options['test']:
            elex_args.append('-t')

        subprocess.run(elex_args, stdout=writefile)

    def load_results(self):
        data = None
        while data is None:
            try:
                data = json.load(open('reup.json'))
            except json.decoder.JSONDecodeError:
                print('Waiting for file to be available.')
                sleep(5)
        return data

    def deconstruct_result(self, result):
        keys = [
            'id', 'raceid',
            'is_ballot_measure', 'electiondate',
            'level', 'statepostal', 'reportingunitname',
            'last', 'officename', 'racetype',
            'winner', 'uncontested', 'runoff',
            'votecount', 'votepct',
            'precinctsreporting', 'precinctsreportingpct', 'precinctstotal',
        ]
        return [result[key] for key in keys]

    def process_result(self, result, tabulated, no_bots):
        """
        Processes top-level (state) results for candidate races, loads data
        into the database  and sends alerts for winning results.
        """
        # Deconstruct result in variables
        (
            ID, RACE_ID,
            IS_BALLOT_MEASURE, ELECTION_DATE,
            LEVEL, STATE_POSTAL, REPORTING_UNIT,
            LAST_NAME, OFFICE_NAME, RACE_TYPE,
            WINNER, UNCONTESTED, RUNOFF,
            VOTE_COUNT, VOTE_PERCENT,
            PRECINCTS_REPORTING, PRECINCTS_REPORTING_PERCENT, PRECINCTS_TOTAL
        ) = self.deconstruct_result(result)

        # Skip ballot measures on non-state-level results
        if IS_BALLOT_MEASURE or LEVEL != DivisionLevel.STATE:
            return

        try:
            ap_meta = APElectionMeta.objects.get(
                ap_election_id=RACE_ID,
            )
        except ObjectDoesNotExist:
            print('No AP Meta found for {0} {1} {2}'.format(
                LAST_NAME, OFFICE_NAME, REPORTING_UNIT
            ))
            return

        id_components = ID.split('-')
        CANDIDATE_ID = '{0}-{1}'.format(
            id_components[1],
            id_components[2]
        )
        if LAST_NAME == 'None of these candidates':
            CANDIDATE_ID = '{0}-{1}'.format(id_components[0], CANDIDATE_ID)

        try:
            candidate = Candidate.objects.get(
                race=ap_meta.election.race,
                ap_candidate_id=CANDIDATE_ID
            )
        except ObjectDoesNotExist:
            print('No Candidate found for {0} {1} {2}'.format(
                LAST_NAME, OFFICE_NAME, REPORTING_UNIT
            ))
            return

        candidate_election = CandidateElection.objects.get(
            election=ap_meta.election,
            candidate=candidate
        )

        division = Division.objects.get(
            level__name=DivisionLevel.STATE,
            code_components__postal=STATE_POSTAL
        )

        filter_kwargs = {
            'candidate_election': candidate_election,
            'division': division
        }

        vote_update = {}

        if not ap_meta.override_ap_votes:
            vote_update['count'] = VOTE_COUNT
            vote_update['pct'] = VOTE_PERCENT

        if not ap_meta.override_ap_call:
            vote_update['winning'] = WINNER
            vote_update['runoff'] = RUNOFF

        if ap_meta.precincts_reporting != PRECINCTS_REPORTING:
            ap_meta.precincts_reporting = PRECINCTS_REPORTING
            ap_meta.precincts_total = PRECINCTS_TOTAL
            ap_meta.precincts_reporting_pct = PRECINCTS_REPORTING_PERCENT

        if PRECINCTS_REPORTING_PERCENT == 1 or UNCONTESTED or tabulated:
            ap_meta.tabulated = True
        else:
            ap_meta.tabulated = False

        ap_meta.save()

        votes = Votes.objects.filter(**filter_kwargs)

        if (WINNER or RUNOFF) and not candidate_election.uncontested:
            # If new call on contested race, send alerts
            first = votes.first()

            if not (first.winning or first.runoff) and not no_bots:
                if ap_meta.election.party:
                    PARTY = ap_meta.election.party.label
                else:
                    PARTY = None
                # TODO: Distinguish a runoff result vs regular primary
                # TODO: Jungle primaries?
                payload = {
                    "race_id": RACE_ID,
                    "election_date": ELECTION_DATE,
                    "division": division.label,
                    "division_slug": division.slug,
                    "office": candidate.race.office.label,
                    "candidate": '{} {}'.format(
                        candidate.person.first_name,
                        candidate.person.last_name
                    ),
                    "primary_party": PARTY,
                    "vote_percent": VOTE_PERCENT,
                    "vote_count": VOTE_COUNT,
                    "runoff": RUNOFF,
                    "precincts_reporting_percent": PRECINCTS_REPORTING_PERCENT,
                    "jungle": RACE_TYPE == 'Open Primary',
                    "runoff_election": RACE_TYPE == 'Runoff',
                    "special_election": 'Special' in RACE_TYPE
                }
                call_race_in_slack.delay(payload)
                call_race_on_twitter.delay(payload)

        votes.update(**vote_update)

    def main(self, options):
        TABULATED = options['tabulated']
        ELECTION_DATE = options['election_date']
        DOWNLOAD = options['download']
        RUN_ONCE = options['run_once']
        NO_BOTS = options['no_bots']
        INTERVAL = app_settings.DATABASE_UPLOAD_DAEMON_INTERVAL

        i = 1
        while True:
            if DOWNLOAD:
                self.download_results(options)

            results = self.load_results()

            for result in tqdm(results):
                self.process_result(result, TABULATED, NO_BOTS)

            if i % 5 == 0:
                call_command('bake_elections', ELECTION_DATE)

            i += 1

            if RUN_ONCE:
                print('Run once specified, exiting.')
                sys.exit(0)

            sleep(INTERVAL)

    def add_arguments(self, parser):
        parser.add_argument('election_date', type=str)
        parser.add_argument(
            '--test',
            dest='test',
            action='store_true',
        )
        parser.add_argument(
            '--download',
            dest='download',
            action='store_true'
        )
        parser.add_argument(
            '--run_once',
            dest='run_once',
            action='store_true'
        )
        parser.add_argument(
            '--tabulated',
            dest='tabulated',
            action='store_true'
        )
        parser.add_argument(
            '--nobots',
            dest='no_bots',
            action='store_true'
        )

    def handle(self, *args, **options):
        self.main(options)
