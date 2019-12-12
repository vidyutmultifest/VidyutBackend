import graphene
from datetime import datetime
from django.db.models import Q

from graphql_jwt.decorators import login_required

from participants.models import Team
from products.models import Product
from products.schema import ProductObj
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
    event = graphene.Field(ProductObj)

    def resolve_event(self, info, **kwargs):
        return Product.objects.values().get(id=self['event'])


class Query(object):
    myRegistrations = graphene.List(EventRegistrationObj, limit=graphene.Int())

    @login_required
    def resolve_myRegistrations(self, info, **kwargs):
        user = info.context.user
        limit = kwargs.get('limit')
        events = EventRegistration.objects.values().filter(Q(user=user) | Q(team__members=user)).order_by("-registrationTimestamp")
        if limit is not None:
            return events[:limit]
        else:
            return events
