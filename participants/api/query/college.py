import graphene

from participants.api.objects import CollegeObj
from participants.models import College


class Query(graphene.ObjectType):
    colleges = graphene.List(CollegeObj)

    @staticmethod
    def resolve_colleges(self, info, **kwargs):
        return College.objects.values().all()
