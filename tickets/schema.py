import graphene

from graphql_jwt.decorators import login_required
from django.utils import timezone
from framework import settings
from access.models import UserAccess
from participants.models import Profile
from payment.models import Order, OrderProduct
from .models import CheckInSession, CheckIn, PhysicalTicket

from tickets.api.stats import Query as TicketStats

to_tz = timezone.get_default_timezone()
from_email = settings.EMAIL_HOST_USER


class TicketGenerationObj(graphene.ObjectType):
    status = graphene.Boolean()
    message = graphene.String()


class IssueTicket(graphene.Mutation):
    class Arguments:
        number = graphene.String(required=False)
        vidyutHash = graphene.String(required=True)

    Output = TicketGenerationObj

    @login_required
    def mutate(self, info, number, vidyutHash):
        issuer = info.context.user
        if UserAccess.objects.get(user=issuer).canIssueTickets:
            user = Profile.objects.get(vidyutHash=vidyutHash)
            if PhysicalTicket.objects.filter(user=user).count() == 0:
                ticketNo = None
                if number is not None:
                    ticketNo = number
                PhysicalTicket.objects.create(
                    issuer=info.context.user,
                    user=user.user,
                    number=ticketNo
                )
                return TicketGenerationObj(status=True, message='Issued Successfully')
            return TicketGenerationObj(status=False, message='Already Issued')
        return TicketGenerationObj(status=False, message='Forbidden. You do not have permission to issue tickets.')


class PerformCheckIn(graphene.Mutation):
    class Arguments:
        sessionID = graphene.String(required=True)
        hash = graphene.String(required=True)

    Output = graphene.Boolean

    @login_required
    def mutate(self, info, sessionID, hash):
        issuer = info.context.user
        user = Profile.objects.get(vidyutHash=hash).user
        access = UserAccess.objects.get(user=issuer)
        session = CheckInSession.objects.get(sessionID=sessionID)
        if access.canCheckInUsers and (session in access.sessionsManaged.all() or access.sessionsManaged.count() == 0):
            if session.allowMultipleCheckIn or CheckIn.objects.filter(
                    user=user,
                    session=session
            ).count() == 0:
                CheckIn.objects.create(
                    user=user,
                    issuer=issuer,
                    session=session
                )
                return True
        return False


class Mutation(object):
    performCheckIn = PerformCheckIn.Field()
    issueTicket = IssueTicket.Field()


# class TicketSoldStatObj(graphene.ObjectType):
#     productID = graphene.String()
#     insiderRollNumbers = graphene.List(graphene.String)
#     buyerHashes = graphene.List(graphene.String)
#
#     def resolve_insiderRollNumbers(self, info):
#         users = Order.objects.filter(orderproduct__product__productID=self.productID).values_list('user', flat=True)
#         return Profile.objects.filter(user__id__in=users, rollNo__isnull=False).values_list('rollNo', flat=True)
#
#     def resolve_buyerHashes(self, info):
#         users = Order.objects.filter(orderproduct__product__productID=self.productID).values_list('user', flat=True)
#         return Profile.objects.filter(user__id__in=users).values_list('vidyutHash', flat=True)


class ValidateTicketObj(graphene.ObjectType):
    status = graphene.Boolean()
    message = graphene.String()
    productName = graphene.String()
    userName = graphene.String()
    rollNo = graphene.String()
    photo = graphene.String()


class Query(TicketStats, graphene.ObjectType):
    validateTicket = graphene.Field(ValidateTicketObj, hash=graphene.String(), sessionID=graphene.String())
    listSessions = graphene.List(graphene.String)

    # viewTicketsSoldStats = graphene.List(TicketSoldStatObj)
    # emailIssuedTicket = graphene.Boolean(ticketID=graphene.String(required=True), email=graphene.String(required=True))

    @login_required
    def resolve_listSessions(self, info, **kwargs):
        return CheckInSession.objects.all().values_list('sessionID', flat=True)

    @login_required
    def resolve_validateTicket(self, info, **kwargs):
        session = CheckInSession.objects.get(sessionID=kwargs.get('sessionID'))
        products = session.products.all()
        profile = Profile.objects.get(vidyutHash=kwargs.get('hash'))
        status = 0
        product = 'n/a'
        message = 'Allow Check-In'
        if session.allowMultipleCheckIn or CheckIn.objects.filter(user=profile.user, session__sessionID=kwargs.get(
                'sessionID')).count() == 0:
            order = Order.objects.filter(
                user=profile.user,
                transaction__isPaid=True,
                products__in=products
            )
            if order.count() == 1:
                product = OrderProduct.objects.get(order=order.first()).product
                status = 1
            else:
                message = 'Not Valid / Not Purchased'
        else:
            message = 'Already Checked-In'
        photo = None
        if profile.photo and hasattr(profile.photo, 'url'):
            photo = info.context.build_absolute_uri(profile.photo.url)
        return ValidateTicketObj(
            status=status,
            message=message,
            userName=profile.user.first_name + ' ' + profile.user.last_name,
            productName=product,
            rollNo=profile.rollNo,
            photo=photo
        )
