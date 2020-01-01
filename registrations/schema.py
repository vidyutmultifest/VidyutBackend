import graphene
from datetime import datetime
from django.db.models import Q

from graphql_jwt.decorators import login_required

from participants.models import Team
from participants.schema import TeamObj
from products.models import Product
from payment.models import Order
from products.schema import ProductObj
from payment.schema import OrderObj
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
            return Order.objects.values().get(id=self['order_id'])
        except Order.DoesNotExist:
            return None


class Query(object):
    myRegistrations = graphene.List(EventRegistrationObj, limit=graphene.Int())
    isAlreadyRegistered = graphene.Boolean(productID=graphene.String(required=True))

    @login_required
    def resolve_myRegistrations(self, info, **kwargs):
        user = info.context.user
        limit = kwargs.get('limit')
        events = EventRegistration.objects.values().filter(Q(user=user) | Q(team__members=user)).order_by("-registrationTimestamp")
        if limit is not None:
            return events[:limit]
        else:
            return events

    @login_required
    def resolve_isAlreadyRegistered(self, info, **kwargs):
        user = info.context.user
        productID = kwargs.get('productID')
        count = EventRegistration.objects.values().filter(Q(event__productID=productID) & (Q(user=user) | Q(team__members=user))).count()
        return count < 1
