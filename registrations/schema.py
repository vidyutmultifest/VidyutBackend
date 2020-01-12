import graphene
from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import Q

from graphql_jwt.decorators import login_required

from access.models import UserAccess
from framework.api.helper import APIException
from participants.api.query.profile import SingleProfileObj
from participants.models import Team, Profile
from participants.api.objects import TeamObj
from products.models import Product
from payment.models import Order
from products.schema import ProductObj
from payment.api.objects import OrderObj, TransactionObj

from .models import EventRegistration


class RegisterObj(graphene.ObjectType):
    regID = graphene.String()


class Register(graphene.Mutation):
    class Arguments:
        productID = graphene.String()
        formData = graphene.String(required=False)
        teamHash = graphene.String(required=False)

    Output = RegisterObj

    @login_required
    def mutate(self, info, productID, formData=None, teamHash=None):
        rObj = EventRegistration.objects.create(
            registrationTimestamp=datetime.now(),
            event=Product.objects.get(productID=productID)
        )
        if formData is not None:
            rObj.formData = formData
        if teamHash is not None:
            rObj.team = Team.objects.get(hash=teamHash)
        else:
            rObj.user = info.context.user
        rObj.save()
        return RegisterObj(regID=rObj.regID)


class Mutation(object):
    register = Register.Field()


class EventRegistrationObj(graphene.ObjectType):
    registrationTimestamp = graphene.String()
    regID = graphene.String()
    team = graphene.Field(TeamObj)
    order = graphene.Field(OrderObj)
    event = graphene.Field(ProductObj)

    def resolve_team(self, info, **kwargs):
        user = info.context.user
        try:
            team = Team.objects.get(id=self['team_id'])
            mlist = []
            for member in team.members.order_by('first_name').all():
                mlist.append({
                    "name": member.first_name + ' ' + member.last_name,
                    "username": member.username
                })
            return TeamObj(
                name=team.name,
                leader={
                    "name": team.leader.first_name + ' ' + team.leader.last_name,
                    "username": team.leader.username
                },
                members=mlist,
                membersCount=len(mlist),
                hash=team.hash,
                isUserLeader=user == team.leader
            )
        except Team.DoesNotExist:
            return None

    def resolve_event(self, info, **kwargs):
        return Product.objects.values().get(id=self['event_id'])

    def resolve_order(self, info, **kwargs):
        try:
            return Order.objects.get(id=self['order_id'])
        except Order.DoesNotExist:
            return None


class RegCountObj(graphene.ObjectType):
    total = graphene.Int()
    paid = graphene.Int()
    paymentPending = graphene.Int()
    amritapurianPaid = graphene.Int()


class RegTeamObj(graphene.ObjectType):
    name = graphene.String()
    leader = graphene.Field(SingleProfileObj)
    members = graphene.List(SingleProfileObj)

    def resolve_leader(self, info):
        if self.leader is not None:
            try:
                return Profile.objects.get(user=self.leader)
            except Profile.DoesNotExist:
                return APIException('Leader profile does not exist in db')

    def resolve_members(self, info):
        return Profile.objects.filter(user__in=self.members.all())


class RegDetailsObj(graphene.ObjectType):
    regID = graphene.String()
    userProfile = graphene.Field(SingleProfileObj)
    teamProfile = graphene.Field(RegTeamObj)
    transaction = graphene.Field(TransactionObj)
    registrationTimestamp = graphene.DateTime()
    formData = graphene.String()

    def resolve_userProfile(self, info):
        if self.user is not None:
            try:
                return Profile.objects.get(user=self.user)
            except Profile.DoesNotExist:
                raise APIException("Profile Does not exist")
        return None

    def resolve_teamProfile(self, info):
        if self.team is not None:
            return Team.objects.get(id=self.team.id)
        return None

    def resolve_transaction(self, info):
        if self.order is not None:
            if self.order.transaction is not None:
                return self.order.transaction
        return None


class RegStatObj(graphene.ObjectType):
    name = graphene.String()
    count = graphene.Field(RegCountObj)
    registrations = graphene.List(RegDetailsObj, isPaid=graphene.Boolean())

    def resolve_name(self, info):
        return self.name

    def resolve_count(self, info):
        regs = EventRegistration.objects.filter(event__id=self.id)
        return {
            "total": regs.count(),
            "paid": regs.filter(order__transaction__isPaid=True).count(),
            "paymentPending": regs.count() - regs.filter(order__transaction__isPaid=True).count(),
            "amritapurianPaid": regs.filter(
                order__transaction__isPaid=True,
                order__user__email__contains='am.students.amrita.edu'
            ).count()
        }

    def resolve_registrations(self, info, **kwargs):
        isPaid = kwargs.get('isPaid')
        product = Product.objects.get(id=self.id)
        if product.competition is not None and product.competition.hasSelectionProcess is True:
            return EventRegistration.objects.filter(event_id=self.id)
        if product.price == 0:
            return EventRegistration.objects.filter(event_id=self.id)
        if isPaid is not None:
            return EventRegistration.objects.filter(event__id=self.id, order__transaction__isPaid=isPaid)
        return EventRegistration.objects.filter(event_id=self.id)


class RegistrationCountObj(graphene.ObjectType):
    total = graphene.Int()
    paid = graphene.Int()
    workshop = graphene.Int()
    workshopPaid = graphene.Int()
    competition = graphene.Int()
    competitionPaid = graphene.Int()
    insider = graphene.Int()
    outsider = graphene.Int()
    insiderPaid = graphene.Int()
    outsiderPaid = graphene.Int()

    def resolve_total(self, info):
        return self.all().count()

    def resolve_paid(self, info):
        return self.filter(order__transaction__isPaid=True).count()

    def resolve_workshop(self, info):
        return self.filter(event__workshop__isnull=False).count()

    def resolve_workshopPaid(self, info):
        return self.filter(event__workshop__isnull=False, order__transaction__isPaid=True).count()

    def resolve_competition(self, info):
        return self.filter(event__competition__isnull=False).count()

    def resolve_competitionPaid(self, info):
        return self.filter(event__competition__isnull=False, order__transaction__isPaid=True).count()

    def resolve_insider(self, info):
        return self.filter(
            (Q(user__email__contains='am.students.amrita.edu') | Q(team__leader__email__contains='am.students.amrita.edu'))
        ).count()

    def resolve_insiderPaid(self, info):
        return self.filter(
            (Q(user__email__contains='am.students.amrita.edu') | Q(team__leader__email__contains='am.students.amrita.edu'))
            & Q(order__transaction__isPaid=True)
        ).count()

    def resolve_outsider(self, info):
        return self.count() - self.filter(
            (Q(user__email__contains='am.students.amrita.edu') | Q(team__leader__email__contains='am.students.amrita.edu'))
        ).count()

    def resolve_outsiderPaid(self, info):
        return self.filter(order__transaction__isPaid=True).count() - self.filter(
            (Q(user__email__contains='am.students.amrita.edu') | Q(team__leader__email__contains='am.students.amrita.edu'))
            & Q(order__transaction__isPaid=True)
        ).count()


class Query(graphene.ObjectType):
    myRegistrations = graphene.List(EventRegistrationObj, limit=graphene.Int())
    isAlreadyRegistered = graphene.Boolean(productID=graphene.String(required=True))
    listRegistrations = graphene.List(RegStatObj, eventType=graphene.String(), eventID=graphene.Int())
    registrationCount = graphene.Field(RegistrationCountObj)

    @login_required
    def resolve_registrationCount(self, info, **kwargs):
        user = info.context.user
        access = UserAccess.objects.get(user=user)
        if access.adminAccess and access.canViewRegistrations:
            if access.productsManaged.count() > 0:
                return EventRegistration.objects.filter(event__in=access.productsManaged.all())
            else:
                return EventRegistration.objects.all()
        else:
            raise APIException('Forbidden')

    @login_required
    def resolve_listRegistrations(self, info, **kwargs):
        user = info.context.user
        access = UserAccess.objects.get(user=user)
        if access.adminAccess and access.canViewRegistrations:
            events = EventRegistration.objects.filter(
                Q(order__transaction__isPaid=True) | Q(event__competition__hasSelectionProcess=True)
                | Q(event__requireAdvancePayment=False)
            ).values_list('event__productID', flat=True)

            if access.productsManaged.count() > 0:
                events = events.filter(event__in=access.productsManaged.all())

            products = Product.objects.filter(requireRegistration=True, productID__in=events)

            eventType = kwargs.get('eventType')
            if eventType is not None:
                if eventType == 'competition':
                    return products.filter(competition__isnull=False)
                elif eventType == 'workshop':
                    return products.filter(workshop__isnull=False)
                elif eventType == 'ticket': #unused case
                    return products.filter(ticket__isnull=False)
                return products

            eventID = kwargs.get('eventType')
            if eventID is not None:
                return products.filter(id=eventID)
            return products
        else:
            raise APIException('Permission Denied')

    @login_required
    def resolve_myRegistrations(self, info, **kwargs):
        user = info.context.user
        limit = kwargs.get('limit')
        events = EventRegistration.objects.values().filter(Q(user=user) | Q(team__members=user)).order_by("-registrationTimestamp")
        if limit is not None:
            return events[:limit]
        return events

    @login_required
    def resolve_isAlreadyRegistered(self, info, **kwargs):
        user = info.context.user
        productID = kwargs.get('productID')
        count = EventRegistration.objects.filter(
            Q(event__productID=productID) &
            (Q(user=user) | Q(team__members=user))
        ).count()
        return count != 0
