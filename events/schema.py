import graphene
from .models import *
from pytz import timezone
from datetime import datetime, timedelta

class DepartmentObj(graphene.ObjectType):
    name = graphene.String()
    slug = graphene.String()


class ContactPersonObj(graphene.ObjectType):
    name = graphene.String()
    phone = graphene.String()
    email = graphene.String()


class EventObj(graphene.ObjectType):
    name = graphene.String()
    slug = graphene.String()
    cover = graphene.String()
    description = graphene.String()
    organizer = graphene.String()
    details = graphene.String()
    fee = graphene.Int()
    isNew = graphene.Boolean()
    isRecommended = graphene.Boolean()
    department = graphene.Field(DepartmentObj)
    contacts = graphene.List(ContactPersonObj)

    def resolve_cover(self, info):
        url = None
        if self['cover'] is not None:
            url = info.context.build_absolute_uri(self['cover'])
        return url

    def resolve_department(self, info):
        return Department.objects.values().get(id=self['dept_id'])

    def resolve_isNew(self, info):
        limit = datetime.now() - timedelta(days=3)
        if self['createdAt'].replace(tzinfo=timezone('Asia/Calcutta')) > limit.replace(tzinfo=timezone('Asia/Calcutta')):
            return True
        return False


class WorkshopObj(EventObj, graphene.ObjectType):
    duration = graphene.String()

    def resolve_contacts(self, info):
        contacts = Workshop.objects.get(slug=self['slug']).contacts
        return contacts.values()


class CompetitionObj(EventObj, graphene.ObjectType):
    entryFee = graphene.Int()
    firstPrize = graphene.String()
    secondPrize = graphene.String()
    thirdPrize = graphene.String()

    def resolve_contacts(self, info):
        contacts = Competition.objects.get(slug=self['slug']).contacts
        return contacts.values()


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
