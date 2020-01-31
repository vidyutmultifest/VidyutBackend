from datetime import datetime

import graphene
from graphql_jwt.decorators import login_required

from payment.models import Transaction, Refund


class RefundTransaction(graphene.Mutation):
    class Arguments:
        transactionID = graphene.String(required=True)
        amount = graphene.Int(required=True)

    Output = graphene.String

    @login_required
    def mutate(self, info, transactionID, amount):
        issuer = info.context.user
        transaction = Transaction.objects.get(transactionID=transactionID)
        if Refund.objects.filter(transaction=transaction).count() == 0:
            refund = Refund.objects.create(
                amount=amount,
                issuer=issuer,
                transaction=transaction,
                timestamp=datetime.now()
            )
            return refund.id
        return None


class Mutation(object):
    refundTransaction = RefundTransaction.Field()

