import graphene

from payment.api.mutation.order import Mutation as OrderMutations
from payment.api.mutation.transaction import Mutation as TransactionMutations
from payment.api.mutation.payment import Mutation as PaymentMutations

from payment.api.query.acrd import Query as ACRDQueries
from payment.api.query.transaction import Query as TransactionQueries
from payment.api.query.order import Query as OrderQueries
from payment.api.query.stats import Query as StatsQueries


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
    pass
