from django.contrib.contenttypes.models import ContentType
from geography.models import Division

from electionnight.models import PageContent, PageType


class ExecutiveOfficeStates(object):
    def bootstrap_executive_office_states(self, election):
        """
        Create state page content exclusively for the U.S. president.
        """
        content_type = ContentType.objects.get_for_model(election.race.office)
        for division in Division.objects.filter(level=self.STATE_LEVEL):
            PageContent.objects.get_or_create(
                content_type=content_type,
                object_id=election.race.office.pk,
                election_day=election.election_day,
                division=division
            )
        # Create national presidential page type
        page_type, created = PageType.objects.get_or_create(
            model_type=ContentType.objects.get(
                app_label='government',
                model='office'
            ),
            election_day=election.election_day,
            division_level=self.NATIONAL_LEVEL,
            jurisdiction=self.FEDERAL_JURISDICTION,
            office=election.race.office,
        )
        PageContent.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(page_type),
            object_id=page_type.pk,
            election_day=election.election_day,
        )
        # Create state results for president page type
        page_type, created = PageType.objects.get_or_create(
            model_type=ContentType.objects.get(
                app_label='government',
                model='office'
            ),
            election_day=election.election_day,
            division_level=self.STATE_LEVEL,
            jurisdiction=self.FEDERAL_JURISDICTION,
            office=election.race.office,
        )
        PageContent.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(page_type),
            object_id=page_type.pk,
            election_day=election.election_day,
        )
