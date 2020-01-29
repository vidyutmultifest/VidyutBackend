import graphene
from django.db.models import Q
from django.utils import timezone
from graphql_jwt.decorators import login_required

from events.models import Workshop, Competition, WorkshopSchedule, CompetitionSchedule
from payment.models import Order
from registrations.models import EventRegistration

to_tz = timezone.get_default_timezone()


class MyScheduleobj(graphene.ObjectType):
    venue = graphene.String()
    start = graphene.String()
    end = graphene.String()

    def resolve_venue(self, info):
        return self.venue

    def resolve_start(self, info):
        return self.slot.startTime.astimezone(to_tz).strftime("%d/%m, %H:%M")

    def resolve_end(self, info):
        return self.slot.endTime.astimezone(to_tz).strftime("%d/%m, %H:%M")


class MyVidyutItemObj(graphene.ObjectType):
    name = graphene.String()
    contact = graphene.String()
    schedule = graphene.List(MyScheduleobj)


class MyVidyutObj(graphene.ObjectType):
    workshops = graphene.List(MyVidyutItemObj)
    tickets = graphene.List(MyVidyutItemObj)
    competitions = graphene.List(MyVidyutItemObj)

    def resolve_workshops(self, info):
        workshops = []
        for t in self['workshops']:
            workshop = Workshop.objects.get(id=t.event.workshop.id)
            workshops.append({
                "name": t.event.name,
                "contact": workshop.contacts.first().name + ' - ' + workshop.contacts.first().phone,
                "schedule": WorkshopSchedule.objects.filter(event=workshop)
            })
        return workshops

    def resolve_competitions(self, info):
        competitions = []
        for t in self['competitions']:
            competition = Competition.objects.get(id=t.event.competition.id)
            competitions.append({
                "name": t.event.name,
                "contact": competition.contacts.first().name + ' - ' + competition.contacts.first().phone,
                "schedule": CompetitionSchedule.objects.filter(event=competition)
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
                    Q(Q(user=user) | Q(team__members=user)) &
                    Q(order__transaction__isPaid=True) &
                    Q(event__competition__isnull=False)
                ),
            "tickets": Order.objects.filter(
                user=user,
                orderproduct__product__ticket__isnull=False,
                transaction__isPaid=True
            )
        }
