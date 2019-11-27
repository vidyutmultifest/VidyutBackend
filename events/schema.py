import graphene
from .models import *


class WorkshopObj(graphene.ObjectType):
    name = graphene.String()
    slug = graphene.String()
    cover = graphene.String()
    description = graphene.String()
    details = graphene.String()
    fee = graphene.Int()

    def resolve_cover(self, info):
        url = None
        if self['cover'] is not None:
            url = info.context.build_absolute_uri(self['cover'])
        return url


class CompetitionObj(WorkshopObj, graphene.ObjectType):
    entryFee = graphene.Int()
    firstPrize = graphene.String()
    secondPrize = graphene.String()
    thirdPrize = graphene.String()


class Query(object):
    getCompetition = graphene.Field(CompetitionObj, slug=graphene.String(required=True))
    listCompetitions = graphene.List(CompetitionObj)
    getWorkshop = graphene.Field(WorkshopObj, slug=graphene.String(required=True))
    listWorkshops = graphene.List(WorkshopObj)

    @staticmethod
    def resolve_getCompetition(self, info, **kwargs):
        slug = kwargs.get('slug')
        return Competition.objects.values().get(slug=slug)

    @staticmethod
    def resolve_listCompetitions(self, info, **kwargs):
        return Competition.objects.values().all()

    @staticmethod
    def resolve_getWorkshop(self, info, **kwargs):
        slug = kwargs.get('slug')
        return Workshop.objects.values().get(slug=slug)

    @staticmethod
    def resolve_listWorkshops(self, info, **kwargs):
        return Workshop.objects.values().all()
