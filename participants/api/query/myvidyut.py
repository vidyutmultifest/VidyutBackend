import graphene
from graphql_jwt.decorators import login_required

from payment.models import Order
from registrations.models import EventRegistration


class MyVidyutItemObj(graphene.ObjectType):
    name = graphene.String()


class MyVidyutObj(graphene.ObjectType):
    workshops = graphene.List(MyVidyutItemObj)
    tickets = graphene.List(MyVidyutItemObj)
    competitions = graphene.List(MyVidyutItemObj)

    def resolve_workshops(self, info):
        workshops = []
        for t in self['workshops']:
            workshops.append({
                "name": t.event.name,
            })
        return workshops

    def resolve_competitions(self, info):
        competitions = []
        for t in self['competitions']:
            competitions.append({
                "name": t.event.name,
            })
        return competitions

    def resolve_tickets(self, info):
        tickets = []
        for t in self['tickets']:
            tickets.append({
                "name": t.products.first().ticket.name,
            })
        return tickets


class Query(graphene.ObjectType):
    myVidyut = graphene.Field(MyVidyutObj)

    @login_required
    def resolve_myVidyut(self, info, **kwargs):
        user = info.context.user
        return {
            "workshops": EventRegistration.objects.filter(
                            user=user,
                            order__transaction__isPaid=True,
                            event__workshop__isnull=False
                        ),
            "competitions": EventRegistration.objects.filter(
                            user=user,
                            order__transaction__isPaid=True,
                            event__competition__isnull=False
                        ),
            "tickets": Order.objects.filter(
                user=user,
                orderproduct__product__ticket__isnull=False,
                transaction__isPaid=True
            )
        }
