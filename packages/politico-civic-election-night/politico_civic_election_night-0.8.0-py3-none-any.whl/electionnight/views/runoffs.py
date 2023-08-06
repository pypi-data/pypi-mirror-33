"""
State result pages.

URL PATTERNS:
/election-results/{YEAR}/{STATE}/
"""
import json

from django.shortcuts import get_object_or_404
from django.urls import reverse
from almanac.models import ElectionEvent
from election.models import ElectionDay
from electionnight.conf import settings
from electionnight.models import PageContent
from electionnight.serializers import ElectionViewSerializer, StateSerializer
from geography.models import Division, DivisionLevel

from .base import BaseView


class RunoffPage(BaseView):
    """
    **Preview URL**: :code:`/state/{YEAR}/{STATE}/{ELECTION_DATE}/`
    """
    name = 'electionnight_state-page'
    path = 'runoff/<int:year>/<slug:state>/<slug:election_date>/'

    js_dev_path = 'electionnight/js/main-runoff-app.js'
    css_dev_path = 'electionnight/css/main-runoff-app.css'

    model = Division
    context_object_name = 'division'
    template_name = 'electionnight/runoffs/index.html'

    def get_queryset(self):
        level = DivisionLevel.objects.get(name=DivisionLevel.STATE)
        return self.model.objects.filter(level=level)

    def get_object(self, **kwargs):
        return get_object_or_404(Division, slug=self.kwargs.get('state'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Set kwargs to properties on class.
        self.division = context['division']
        self.year = self.kwargs.get('year')
        self.state = self.kwargs.get('state')
        self.election_date = self.kwargs.get('election_date')
        context['secret'] = settings.SECRET_KEY
        context['year'] = self.year
        context['state'] = self.state
        context['election_date'] = self.election_date
        context['content'] = PageContent.objects.division_content(
            ElectionDay.objects.get(date=self.election_date),
            self.division
        )
        context['subpath'] = '/runoff/'

        template = {
            **context,
            **self.get_paths_context(production=context['production']),
            **self.get_elections_context(context['division']),
        }

        nav, nav_json = self.get_nav_links(context['subpath'])
        template['nav'] = nav
        template['nav_json'] = nav_json

        return template

    def get_nav_links(self, subpath='/runoff/'):
        todays_elections = ElectionEvent.objects.filter(
            election_day__date=self.election_date,
            event_type__in=[ElectionEvent.PRIMARIES, ElectionEvent.GENERAL]
        ).values_list('division__label', flat=True)

        todays_runoffs = ElectionEvent.objects.filter(
            election_day__date=self.election_date,
            event_type__in=[
                ElectionEvent.PRIMARIES_RUNOFF, ElectionEvent.GENERAL_RUNOFF
            ]
        ).values_list('division__label', flat=True)

        state_level = DivisionLevel.objects.get(name=DivisionLevel.STATE)
        # All states except DC
        states = Division.objects.filter(
            level=state_level,
        ).exclude(code='11').order_by('label')
        # Nav links should always refer to main state page. We can use subpath
        # to determine how deep publish path is relative to state pages.
        relative_prefix = ''
        print(subpath)

        depth = subpath.lstrip('/').count('/')
        print(depth)
        for i in range(depth):
            relative_prefix += '../'
        data = {
            'states': [
                {
                    'link': '../{0}{1}/'.format(
                        relative_prefix,
                        state.slug
                    ),
                    'name': state.label,
                    'live': state.label in todays_elections,
                    'runoff': state.label in todays_runoffs
                } for state in states
            ],
        }

        return data, json.dumps(data)

    def get_elections_context(self, division):
        elections_context = {}

        election_day = ElectionDay.objects.get(date=self.election_date)

        governor_elections = list(division.elections.filter(
            election_day=election_day,
            race__office__slug__contains='governor'
        ))
        senate_elections = list(division.elections.filter(
            election_day=election_day,
            race__office__body__slug__contains='senate'
        ))

        house_elections = {}
        district = DivisionLevel.objects.get(name=DivisionLevel.DISTRICT)
        for district in division.children.filter(
            level=district
        ).order_by('code'):
            district_elections = list(district.elections.filter(
                election_day=election_day
            ))
            serialized = ElectionViewSerializer(
                district_elections, many=True
            ).data

            house_elections[district.label] = serialized

        elections_context['governor_elections'] = ElectionViewSerializer(
            governor_elections, many=True
        ).data

        elections_context['senate_elections'] = ElectionViewSerializer(
            senate_elections, many=True
        ).data

        elections_context['house_elections'] = house_elections

        return elections_context

    def get_publish_path(self):
        return 'election-results/{}/{}/runoff/'.format(self.year, self.state)

    def get_serialized_context(self):
        """Get serialized context for baking to S3."""
        division = Division.objects.get(slug=self.state)
        return StateSerializer(division, context={
            'election_date': self.election_date
        }).data

    def get_extra_static_paths(self, production):
        division = Division.objects.get(slug=self.state)
        geo = (
            'election-results/cdn/geography/us-census/cb/500k/2016/states/{0}/{0}'
        ).format(division.code)
        if (production and
           settings.AWS_S3_BUCKET == 'interactives.politico.com'):
            return {
                'context': 'context.json',
                'geo_county': (
                    'https://www.politico.com/'
                    '{}-county.json').format(geo),
                'geo_district': (
                    'https://www.politico.com/'
                    '/{}-district.json').format(geo),
            }
        elif (production and
              settings.AWS_S3_BUCKET != 'interactives.politico.com'):
            return {
                'context': 'context.json',
                'geo_county': (
                    'https://s3.amazonaws.com/'
                    'interactives.politico.com/{}-county.json').format(geo),
                'geo_district': (
                    'https://s3.amazonaws.com/'
                    'interactives.politico.com/{}-district.json').format(geo),
            }
        return {
            'context': reverse(
                'electionnight_api_state-election-detail',
                args=[self.election_date, self.object.pk],
            ),
            'geo_county': (
                'https://s3.amazonaws.com/'
                'interactives.politico.com/{}-county.json').format(geo),
            'geo_district': (
                'https://s3.amazonaws.com/'
                'interactives.politico.com/{}-district.json').format(geo),
        }
