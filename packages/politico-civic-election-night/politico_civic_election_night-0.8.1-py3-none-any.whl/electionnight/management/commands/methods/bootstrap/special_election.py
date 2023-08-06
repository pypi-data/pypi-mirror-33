from django.contrib.contenttypes.models import ContentType
from geography.models import DivisionLevel

from electionnight.models import PageContent, PageType


class SpecialElection(object):
    def bootstrap_special_election(self, election):
        division = election.division
        content_type = ContentType.objects.get_for_model(division)
        office_division = election.race.office.division
        PageContent.objects.get_or_create(
            content_type=content_type,
            object_id=election.division.pk,
            election_day=election.election_day,
            special_election=True,
        )
        # Senate seats
        if office_division.level.name == DivisionLevel.STATE:
            PageContent.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(
                    office_division
                ),
                object_id=office_division.pk,
                election_day=election.election_day,
            )
        # House seats
        elif office_division.level.name == DivisionLevel.DISTRICT:
            PageContent.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(
                    office_division.parent
                ),
                object_id=office_division.parent.pk,
                election_day=election.election_day,
            )
        # Generic state pages, type and content
        page_type, created = PageType.objects.get_or_create(
            model_type=ContentType.objects.get(
                app_label='geography',
                model='division'
            ),
            election_day=election.election_day,
            division_level=DivisionLevel.objects.get(name=DivisionLevel.STATE),
        )
        PageContent.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(
                page_type
            ),
            object_id=page_type.pk,
            election_day=election.election_day,
        )
