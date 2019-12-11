import json

import graphene
from .models import *
from pytz import timezone
from datetime import datetime, timedelta
from products.models import *

from .api.partners import Query as PartnerQueries


class DepartmentObj(graphene.ObjectType):
    name = graphene.String()
    slug = graphene.String()


class ContactPersonObj(graphene.ObjectType):
    name = graphene.String()
    phone = graphene.String()
    email = graphene.String()


class FormFieldObj(graphene.ObjectType):
    key = graphene.String()
    label = graphene.String()
    type = graphene.String()


class BasicProductDetailsObj(graphene.ObjectType):
    productID = graphene.String()
    price = graphene.String()

    def resolve_productID(self, info):
        return self


class EventObj(graphene.ObjectType):
    name = graphene.String()
    slug = graphene.String()
    cover = graphene.String()
    description = graphene.String()
    organizer = graphene.String()
    details = graphene.String()
    fee = graphene.Int()
    isNew = graphene.Boolean()
    isTeamEvent = graphene.Boolean()
    hasSelectionProcess = graphene.Boolean()
    minTeamSize = graphene.Int()
    maxTeamSize = graphene.Int()
    isRecommended = graphene.Boolean()
    department = graphene.Field(DepartmentObj)
    contacts = graphene.List(ContactPersonObj)
    productID = graphene.String()
    products = graphene.List(BasicProductDetailsObj)

    def resolve_cover(self, info):
        url = None
        if self['cover'] is not '':
            url = info.context.build_absolute_uri(self['cover'])
        return url

    def resolve_department(self, info):
        return Department.objects.values().get(id=self['dept_id'])

    def resolve_isNew(self, info):
        limit = datetime.now() - timedelta(days=3)
        if self['createdAt'].replace(tzinfo=timezone('Asia/Calcutta')) > limit.replace(tzinfo=timezone('Asia/Calcutta')):
            return True
        return False


class TicketObj(EventObj, graphene.ObjectType):

    def resolve_productID(self, info):
        products = Product.objects.filter(ticket_id=self['id'])
        if products.count() > 0:
            return products.first().productID

    def resolve_products(self, info):
        return Product.objects.values_list('productID', flat=True).filter(ticket_id=self['id'])


class MerchandiseObj(EventObj, graphene.ObjectType):

    def resolve_productID(self, info):
        products = Product.objects.filter(merchandise_id=self['id'])
        if products.count() > 0:
            return products.first().productID

    def resolve_products(self, info):
        return Product.objects.values_list('productID', flat=True).filter(merchandise_id=self['id'])


class WorkshopObj(EventObj, graphene.ObjectType):
    duration = graphene.String()

    def resolve_contacts(self, info):
        contacts = Workshop.objects.get(slug=self['slug']).contacts
        return contacts.values()

    def resolve_productID(self, info):
        products = Product.objects.filter(workshop_id=self['id'])
        if products.count() > 0:
            return products.first().productID

    def resolve_products(self, info):
        return Product.objects.values_list('productID', flat=True).filter(workshop_id=self['id'])


class CompetitionObj(EventObj, graphene.ObjectType):
    entryFee = graphene.Int()
    firstPrize = graphene.String()
    secondPrize = graphene.String()
    thirdPrize = graphene.String()
    formFields = graphene.List(FormFieldObj)

    def resolve_contacts(self, info):
        contacts = Competition.objects.get(slug=self['slug']).contacts
        return contacts.values()

    def resolve_productID(self, info):
        products = Product.objects.filter(competition_id=self['id'])
        if products.count() > 0:
            return products.first().productID

    def resolve_products(self, info):
        return Product.objects.values_list('productID', flat=True).filter(competition_id=self['id'])

    def resolve_formFields(self, info):
        if self['formFields'] is not '' and self['formFields'] is not None:
            return json.loads(self['formFields'])
        return None


class Query(PartnerQueries, object):
    getCompetition = graphene.Field(CompetitionObj, slug=graphene.String(required=True))
    getWorkshop = graphene.Field(WorkshopObj, slug=graphene.String(required=True))
    getTicketEvent = graphene.Field(TicketObj, slug=graphene.String(required=True))
    getMerchandise = graphene.Field(MerchandiseObj, slug=graphene.String(required=True))
    listCompetitions = graphene.List(CompetitionObj)
    listWorkshops = graphene.List(WorkshopObj)
    listMerchandise = graphene.List(MerchandiseObj)
    listTicketEvents = graphene.List(TicketObj)
    listTeamCompetitions = graphene.List(CompetitionObj)

    @staticmethod
    def resolve_getCompetition(self, info, **kwargs):
        slug = kwargs.get('slug')
        return Competition.objects.values().get(slug=slug)

    @staticmethod
    def resolve_listCompetitions(self, info, **kwargs):
        return Competition.objects.values().all()

    @staticmethod
    def resolve_listTeamCompetitions(self, info, **kwargs):
        return Competition.objects.values().filter(isTeamEvent=True)

    @staticmethod
    def resolve_getWorkshop(self, info, **kwargs):
        slug = kwargs.get('slug')
        return Workshop.objects.values().get(slug=slug)

    @staticmethod
    def resolve_listWorkshops(self, info, **kwargs):
        return Workshop.objects.values().all()

    @staticmethod
    def resolve_getMerchandise(self, info, **kwargs):
        slug = kwargs.get('slug')
        return Merchandise.objects.values().get(slug=slug)

    @staticmethod
    def resolve_listMerchandise(self, info, **kwargs):
        return Merchandise.objects.values().all()

    @staticmethod
    def resolve_getTicketEvent(self, info, **kwargs):
        slug = kwargs.get('slug')
        return Ticket.objects.values().get(slug=slug)

    @staticmethod
    def resolve_listTicketEvents(self, info, **kwargs):
        return Ticket.objects.values().all()
