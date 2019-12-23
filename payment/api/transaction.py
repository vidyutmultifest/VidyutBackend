import graphene
from datetime import datetime
from graphql_jwt.decorators import login_required
from django.utils import timezone

from payment.models import Transaction, Order, OrderProduct

to_tz = timezone.get_default_timezone()


class TransactionInitObj(graphene.ObjectType):
    transactionID = graphene.String()


class InitiateTransaction(graphene.Mutation):
    class Arguments:
        orderID = graphene.String(required=True)
        isOnline = graphene.Boolean(required=False)

    Output = TransactionInitObj

    @login_required
    def mutate(self, info, orderID, isOnline=False):
        customer = info.context.user
        try:
            order = Order.objects.get(orderID=orderID)
        except Order.DoesNotExist:
            return None
            # TODO : throw error as order doresnt exist

        cost = 0
        for product in OrderProduct.objects.filter(order=order):
            cost = cost + product.price * product.qty
            # Add GST Amount
            if isOnline and not product.product.isGSTAccounted:
                cost = cost + 0.18 * cost

        # TODO : subtract promocode value from amount

        # Create a transaction with current timestamp
        timestamp = datetime.now().astimezone(to_tz)
        obj = Transaction.objects.create(
            amount=int(cost),
            isPaid=False,
            isProcessed=False,
            isPending=False,
            manualIssue=False,
            isOnline=isOnline,
            timestamp=timestamp,
            user=customer
        )

        # Link newly created transaction with the existing order
        order.transaction = obj
        order.save()

        return TransactionInitObj(transactionID=obj.transactionID)


class Mutation(object):
    initiateTransaction = InitiateTransaction.Field()
