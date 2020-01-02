import graphene
from graphql_jwt.decorators import login_required
from datetime import datetime
from django.utils import timezone

from access.models import UserAccess
from payment.models import Transaction

to_tz = timezone.get_default_timezone()


class OrderStatusObj(graphene.ObjectType):
    status = graphene.Boolean()


class CollectPayment(graphene.Mutation):
    class Arguments:
        status = graphene.String(required=True)
        transactionID = graphene.String(required=True)
        deviceDetails = graphene.String(required=True)
        location = graphene.String(required=True)

    Output = OrderStatusObj

    @login_required
    def mutate(self, info, status, transactionID, deviceDetails, location):
        issuer = info.context.user
        if UserAccess.objects.get(user=issuer).canAcceptPayment:
            t = Transaction.objects.get(transactionID=transactionID)
            if t.isPaid is False:
                timestamp = datetime.now().astimezone(to_tz)
                t.isProcessed = True
                if status == "paid":
                    t.isPaid = True
                    t.isPending = False
                elif status == "reject":
                    t.isPaid = False
                    t.isPending = False
                elif status == "pending":
                    t.isPaid = False
                    t.isPending = True
                t.manualIssue = True
                t.issuerDevice = deviceDetails
                t.issuerLocation = location
                t.issuer = issuer
                t.timestamp = timestamp
                t.save()
                return {"status": True}
        return {"status": False}


class Mutation(graphene.ObjectType):
    collectPayment = CollectPayment.Field()
