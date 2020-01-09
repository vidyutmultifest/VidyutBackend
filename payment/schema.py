import graphene
from django.db.models import Sum
from graphql_jwt.decorators import login_required

from access.models import UserAccess
from payment.api.mutation.order import Mutation as OrderMutations
from payment.api.mutation.transaction import Mutation as TransactionMutations
from payment.api.mutation.payment import Mutation as PaymentMutations

from payment.api.query.acrd import Query as ACRDQueries
from payment.api.query.transaction import Query as TransactionQueries
from payment.api.query.order import Query as OrderQueries
from payment.api.query.stats import Query as StatsQueries
from payment.models import Transaction


class Mutation(
    OrderMutations,
    TransactionMutations,
    PaymentMutations,
    graphene.ObjectType
):
    pass


class Query(
    ACRDQueries,
    OrderQueries,
    TransactionQueries,
    StatsQueries,
    graphene.ObjectType
):
    getAmountCollected = graphene.Int()
    getTransactionsApprovedCount = graphene.Int()
    getTransactionsPendingCount = graphene.Int()

    @login_required
    def resolve_getAmountCollected(self, info, **kwargs):
        user = info.context.user
        if UserAccess.objects.get(user=user).canAcceptPayment:
            return Transaction.objects.filter(issuer=user, isPaid=True).aggregate(Sum('amount'))['amount__sum']

    @login_required
    def resolve_getTransactionsApprovedCount(self, info, **kwargs):
        user = info.context.user
        if UserAccess.objects.get(user=user).canAcceptPayment:
            return Transaction.objects.filter(issuer=user, isPaid=True).count()

    @login_required
    def resolve_getTransactionsPendingCount(self, info, **kwargs):
        user = info.context.user
        if UserAccess.objects.get(user=user).canAcceptPayment:
            return Transaction.objects.filter(issuer=user, isPending=True).count()