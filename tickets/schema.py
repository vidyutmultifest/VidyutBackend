import graphene

from graphql_jwt.decorators import login_required
from django.utils import timezone
from framework import settings
from access.models import UserAccess
from framework.api.helper import APIException
from participants.models import Profile
from payment.models import Order, OrderProduct, Product
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
            user = Profile.objects.get(vidyutHash=vidyutHash).user
            if PhysicalTicket.objects.filter(user=user).count() == 0:
                ticketNo = None
                if number is not None:
                    ticketNo = number
                PhysicalTicket.objects.create(
                    issuer=info.context.user,
                    user=user,
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


class SessionObj(graphene.ObjectType):
    name = graphene.String()
    sessionID = graphene.String()
    isActive = graphene.Boolean()
    products = graphene.List(graphene.String)
    checkInCount = graphene.Int()
    issuerCount = graphene.Int()

    def resolve_products(self, info):
        return Product.objects.filter(id__in=self.products.all()).values_list('name', flat=True)

    def resolve_checkInCount(self, info):
        return CheckIn.objects.filter(session__sessionID=self.sessionID).count()

    def resolve_issuerCount(self, info):
        return CheckIn.objects.filter(session__sessionID=self.sessionID).values_list('issuer_id', flat=True).distinct().count()


class ValidateTicketObj(graphene.ObjectType):
    status = graphene.Boolean()
    message = graphene.String()
    productName = graphene.String()
    userName = graphene.String()
    rollNo = graphene.String()
    photo = graphene.String()
    tShirtSize = graphene.String()
    isProfileComplete = graphene.Boolean()


class Query(TicketStats, graphene.ObjectType):
    checkForTicket = graphene.Field(ValidateTicketObj, hash=graphene.String())
    validateTicket = graphene.Field(ValidateTicketObj, hash=graphene.String(), sessionID=graphene.String())
    listSessions = graphene.List(SessionObj)

    @login_required
    def resolve_listSessions(self, info, **kwargs):
        return CheckInSession.objects.all()

    @login_required
    def resolve_checkForTicket(self, info, **kwargs):
        profile = Profile.objects.get(vidyutHash=kwargs.get('hash'))
        if UserAccess.objects.get(user=info.context.user).canIssueTickets:
            order = Order.objects.filter(
                user=profile.user,
                transaction__isPaid=True,
                products__name__contains='Revel'
            )
            status = False
            product = None
            photo = None
            isProfileComplete = True
            if order.count() == 1:
                product = order.first().products.all().first().name
                if PhysicalTicket.objects.filter(user=profile.user).count() == 0:
                    status = True
                    message = 'Eligible for ticket - ' + product
                    profilemsg = 'Profile Incomplete - '
                    if not profile.photo or not hasattr(profile.photo, 'url'):
                        isProfileComplete = False
                        profilemsg += ' Selfie, '
                    if profile.gender is None or len(profile.gender) < 1:
                        isProfileComplete = False
                        profilemsg += ' Gender, '
                    if profile.phone is None or len(profile.phone) < 10:
                        isProfileComplete = False
                        profilemsg += ' Phone No., '
                    if profile.rollNo is None or len(profile.rollNo) < 5:
                        isProfileComplete = False
                        profilemsg += ' Roll No., '
                    if profile.college is None:
                        isProfileComplete = False
                        profilemsg += ' College Name, '
                    if profile.shirtSize is None or len(profile.shirtSize) < 1:
                        isProfileComplete = False
                        profilemsg += ' T-Shirt Size, '
                    profilemsg += ' to be updated'
                    if isProfileComplete is False:
                        status = False
                        message = profilemsg
                else:
                    message = 'Ticket already given.'
            else:
                message = 'No ticket exists for the user'
            if profile.photo and hasattr(profile.photo, 'url'):
                photo = info.context.build_absolute_uri(profile.photo.url)
            return ValidateTicketObj(
                status=status,
                message=message,
                userName=profile.user.first_name + ' ' + profile.user.last_name,
                productName=product,
                rollNo=profile.rollNo,
                tShirtSize=profile.shirtSize,
                photo=photo,
                isProfileComplete=isProfileComplete
            )
        raise APIException('Permission denied.')

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
            tShirtSize=profile.shirtSize,
            photo=photo
        )
