import csv

from django.core.management.base import BaseCommand

from vote.models import Votes


class Command(BaseCommand):
    help = 'Gets state-level House results'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        state_votes = Votes.objects.filter(
            division__level__slug='state',
            candidate_election__election__division__level__slug='district',
        ).order_by(
            'division__label',
            'candidate_election__election__division__code',
            'candidate_election__candidate__party__label'
        )

        with open('test.csv', 'w') as f:
            writer = csv.writer(f)
            header_row = [
                'State',
                'District',
                'First',
                'Last',
                'Party',
                'Winner',
                'Runoff'
            ]
            writer.writerow(header_row)

            for votes in state_votes:
                row = [
                    votes.division.label,
                    votes.candidate_election.election.division.code,
                    votes.candidate_election.candidate.person.first_name,
                    votes.candidate_election.candidate.person.last_name,
                    votes.candidate_election.candidate.party.label,
                    votes.winning,
                    votes.runoff
                ]

                writer.writerow(row)
