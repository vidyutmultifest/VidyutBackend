import graphene
from datetime import datetime


from django.core.mail import send_mail
from django.template.loader import get_template
from django.utils.html import strip_tags
from graphql_jwt.decorators import login_required
from django.utils import timezone
from framework import settings
from access.models import UserAccess
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


class Query(object):
    emailIssuedTicket = graphene.Boolean(ticketID=graphene.String(required=True), email=graphene.String(required=True))

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
                    'image': tObj.product.product.cover,
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
