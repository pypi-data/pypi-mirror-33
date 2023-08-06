from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import Q
from election.models import ElectionDay
from electionnight.views import RunoffPage, SpecialElectionPage, StatePage
from geography.models import DivisionLevel
from tqdm import tqdm


# TODO: Clean this up and split methods out...
class Command(BaseCommand):
    help = 'Publishes an election!'

    def add_arguments(self, parser):
        parser.add_argument(
            'election_dates',
            nargs='+',
            help="Election dates to publish."
        )

    def fetch_states(self, elections, runoff=False):
        """
        Returns the unique divisions for all elections on an election day.
        """
        district_level = DivisionLevel.objects.get(name=DivisionLevel.DISTRICT)

        states = []

        for election in elections:
            # skip runoffs if a state page
            if election.election_type.is_runoff() and not runoff:
                continue

            # only get runoffs if a runoff page
            if not election.election_type.is_runoff() and runoff:
                continue

            if election.division.level == district_level:
                division = election.division.parent
            else:
                division = election.division

            states.append(division)

        return list(set(states))

    def bake_runoff_pages(self, elections):
        states = self.fetch_states(elections, runoff=True)
        self.stdout.write(self.style.SUCCESS('Baking runoff pages.'))
        for state in tqdm(states):
            self.stdout.write('> {}'.format(state.name))
            kwargs = {
                'state': state.slug,
                'year': self.ELECTION_DAY.cycle.slug,
                'election_date': str(self.ELECTION_DAY.date)
            }
            view = RunoffPage(**kwargs)
            view.publish_statics()
            view.publish_template(**kwargs)

    def bake_state_pages(self, elections):
        states = self.fetch_states(elections)
        self.stdout.write(self.style.SUCCESS('Baking state pages.'))
        for state in tqdm(states):
            self.stdout.write('> {}'.format(state.name))
            kwargs = {
                'state': state.slug,
                'year': self.ELECTION_DAY.cycle.slug,
                'election_date': str(self.ELECTION_DAY.date)
            }
            view = StatePage(**kwargs)
            view.publish_statics()
            view.publish_template(**kwargs)

            sample_election = elections.filter(division=state).first()

            if not sample_election:
                sample_election = elections.filter(
                    division__in=state.children.all()
                ).first()

            if sample_election.election_type.is_primary():
                view.publish_statics(subpath='primary/')
                view.publish_template(subpath='primary/', **kwargs)
            # TODO: If general or primary runoff...

    def bake_special_page(self, election):
        states = self.fetch_states([election])
        self.stdout.write(self.style.SUCCESS('Baking special pages.'))
        for state in tqdm(states):
            self.stdout.write('> {}'.format(state.name))
            kwargs = {
                'state': state.slug,
                'year': self.ELECTION_DAY.cycle.slug,
                'month': self.ELECTION_DAY.date.strftime('%b').lower(),
                'day': self.ELECTION_DAY.date.strftime('%d').lower(),
                'election_date': str(self.ELECTION_DAY.date)
            }
            view = SpecialElectionPage(**kwargs)
            view.publish_statics()
            view.publish_template(**kwargs)

    def handle(self, *args, **options):
        election_dates = options['election_dates']
        for date in election_dates:
            election_day = ElectionDay.objects.get(
                date=date
            )
            self.ELECTION_DAY = election_day
            elections = election_day.elections.filter(race__special=False)
            specials = election_day.elections.filter(race__special=True)
            self.bake_state_pages(elections)
            self.bake_runoff_pages(elections)

            if len(specials) > 0:
                for special in specials:
                    if special.division.level.name == DivisionLevel.STATE:
                        state = special.division
                    elif special.division.level.name == DivisionLevel.DISTRICT:
                        state = special.division.parent

                    check_elections = elections.filter(
                        Q(division=state) | Q(division__parent=state)
                    )

                    if len(check_elections) > 0:
                        print(
                            'No special election page for {}'.format(
                                special.race
                            )
                        )
                        continue
                    else:
                        self.bake_special_page(special)
