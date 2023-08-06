from django.contrib.contenttypes.models import ContentType
from django.core import exceptions
from django.db import models


class PageContentManager(models.Manager):
    """
    Custom manager adds methods to serialize related content blocks.
    """
    @staticmethod
    def serialize_content_blocks(page_content):
        return {
            block.content_type.slug: block.content for block in
            page_content.blocks.all()
        }

    def office_content(self, election_day, office):
        """
        Return serialized content for an office page.
        """
        from electionnight.models import PageType
        office_type = ContentType.objects.get_for_model(office)
        page_type = PageType.objects.get(
            model_type=office_type,
            election_day=election_day,
            division_level=office.division.level,
        )

        page_content = self.get(
            content_type__pk=office_type.pk,
            object_id=office.pk,
            election_day=election_day
        )
        page_type_content = self.get(
            content_type=ContentType.objects.get_for_model(page_type),
            object_id=page_type.pk,
            election_day=election_day
        )
        return {
            "page": self.serialize_content_blocks(page_content),
            "page_type": self.serialize_content_blocks(page_type_content),
        }

    def body_content(self, election_day, body, division=None):
        """
        Return serialized content for a body page.
        """
        body_type = ContentType.objects.get_for_model(body)

        kwargs = {
            'content_type__pk': body_type.pk,
            'object_id': body.pk,
            'election_day': election_day,
        }

        if division:
            kwargs['division'] = division

        content = self.get(**kwargs)
        return {
            'page': self.serialize_content_blocks(content),
            'page_type': None  # TODO
        }

    def division_content(self, election_day, division):
        """
        Return serialized content for a division page.
        """
        from electionnight.models import PageType
        division_type = ContentType.objects.get_for_model(division)
        page_type = PageType.objects.get(
            model_type=division_type,
            election_day=election_day,
            division_level=division.level,
        )

        page_content = self.get(
            content_type__pk=division_type.pk,
            object_id=division.pk,
            election_day=election_day
        )
        page_type_content = self.get(
            content_type=ContentType.objects.get_for_model(page_type),
            object_id=page_type.pk,
            election_day=election_day,
        )
        return {
            'page': self.serialize_content_blocks(page_content),
            'page_type': self.serialize_content_blocks(page_type_content),
        }
