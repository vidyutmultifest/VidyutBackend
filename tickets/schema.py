import graphene
from datetime import datetime


from django.core.mail import send_mail
from django.template.loader import get_template
from django.utils.html import strip_tags
from graphql_jwt.decorators import login_required
from django.utils import timezone
from framework import settings
from access.models import UserAccess
from participants.models import Profile
from payment.models import Order
from products.models import Product
from .models import Ticket

to_tz = timezone.get_default_timezone()
from_email = settings.EMAIL_HOST_USER


class SalesTicketObj(graphene.ObjectType):
    ticketID = graphene.String()
    purchaseTimestamp = graphene.String()


class IssueTicket(graphene.Mutation):
    class Arguments:
        productID = graphene.String(required=True)

    Output = SalesTicketObj

    @login_required
    def mutate(self, info, productID):
        issuer = info.context.user
        if UserAccess.objects.get(user=issuer).canIssueTickets:
            product = Product.objects.get(productID=productID)
            purchaseTimestamp = datetime.now().astimezone(to_tz)
            ticketObj = Ticket.objects.create(product=product, purchaseTimestamp=purchaseTimestamp, purchaser=issuer)
            return SalesTicketObj(ticketID=ticketObj.ticketID, purchaseTimestamp=purchaseTimestamp)
        return None


class Mutation(object):
    issueTicket = IssueTicket.Field()

#
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
#         return Profile.objects.filter(user__id__in=users, rollNo__isnull=False).values_list('vidyutHash', flat=True)


class ValidateTicketObj(graphene.ObjectType):
    status = graphene.Boolean()
    productName = graphene.String()
    userName = graphene.String()
    rollNo = graphene.String()
    photo = graphene.String()


class Query(object):
    validateTicket = graphene.Field(ValidateTicketObj, hash=graphene.String(), productID=graphene.String())
    # viewTicketsSoldStats = graphene.List(TicketSoldStatObj)
    emailIssuedTicket = graphene.Boolean(ticketID=graphene.String(required=True), email=graphene.String(required=True))

    @login_required
    def resolve_validateTicket(self, info, **kwargs):
        product = Product.objects.get(productID=kwargs.get('productID'))
        profile = Profile.objects.get(vidyutHash=kwargs.get('hash'))
        order = Order.objects.filter(
            user=profile.user,
            transaction__isPaid=True,
            products=product
        )
        status = 0
        if order.count() == 1:
            status = 1
        photo = None
        if profile.photo and hasattr(profile.photo, 'url'):
            photo = info.context.build_absolute_uri(profile.photo.url)
        return ValidateTicketObj(
            status=status,
            userName=profile.user.first_name + ' ' + profile.user.last_name,
            productName=product.name,
            rollNo=profile.rollNo,
            photo=photo
        )

    # @login_required
    # def resolve_viewTicketsSoldStats(self, info, **kwargs):
    #     return Product.objects.filter(ticket__isnull=False)

    @login_required
    def resolve_emailIssuedTicket(self, info, **kwargs):
        issuer = info.context.user
        if UserAccess.objects.get(user=issuer).canIssueTickets:
            email = kwargs.get('email')
            ticketID = kwargs.get('ticketID')
            try:
                tObj = Ticket.objects.get(ticketID=ticketID, purchaser=issuer, isCounterTicket=True, isActive=False)
                htmly = get_template('./emails/email-issued-ticket.html')
                d = {
                    'ticketID': str(tObj.ticketID),
                    'image':  info.context.build_absolute_uri(tObj.product.product.cover.url),
                    'productName': str(tObj.product.product.name),
                    'amount': str(tObj.product.product.fee),
                    'purchaser': tObj.purchaser.first_name
                }
                html_content = htmly.render(d)
                send_mail(
                    'You have received a pass for the ' + str(tObj.product.product.name),
                    strip_tags(html_content),
                    from_email,
                    [email],
                    html_message=html_content,
                    fail_silently=False,
                )
                return True
            except Ticket.DoesNotExist:
                return False
        return None
