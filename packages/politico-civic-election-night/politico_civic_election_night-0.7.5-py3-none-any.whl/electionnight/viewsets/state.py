from election.models import ElectionDay
from geography.models import Division, DivisionLevel
from rest_framework import generics
from rest_framework.exceptions import APIException

from electionnight.serializers import StateListSerializer, StateSerializer


class StateMixin(object):
    def get_queryset(self):
        """
        Returns a queryset of all states holding a non-special election on
        a date.
        """
        try:
            date = ElectionDay.objects.get(date=self.kwargs['date'])
        except Exception:
            raise APIException(
                'No elections on {}.'.format(self.kwargs['date'])
            )
        division_ids = []

        normal_elections = date.elections.filter(race__special=False)

        if len(normal_elections) > 0:
            for election in date.elections.all():
                if election.division.level.name == DivisionLevel.STATE:
                    division_ids.append(election.division.uid)
                elif election.division.level.name == DivisionLevel.DISTRICT:
                    division_ids.append(election.division.parent.uid)

        return Division.objects.filter(uid__in=division_ids)

    def get_serializer_context(self):
        """Adds ``election_day`` to serializer context."""
        context = super(StateMixin, self).get_serializer_context()
        context['election_date'] = self.kwargs['date']
        return context


class StateList(StateMixin, generics.ListAPIView):
    serializer_class = StateListSerializer


class StateDetail(StateMixin, generics.RetrieveAPIView):
    serializer_class = StateSerializer
