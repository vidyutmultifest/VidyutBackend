import graphene
from .models import *
from graphql_jwt.decorators import login_required
from products.schema import ProductObj
from pytz import timezone


class TransactionObj(graphene.ObjectType):
    transactionID = graphene.String()
    timestamp = graphene.String()
    amount = graphene.String()

    def resolve_timestamp(self, info):
        return self['timestamp'].replace(tzinfo=timezone('Asia/Calcutta'))


class OrderObj(graphene.ObjectType):
    orderID = graphene.String()
    timestamp = graphene.String()
    products = graphene.List(ProductObj)
    transaction = graphene.Field(TransactionObj)

    def resolve_timestamp(self, info):
        return self['timestamp'].replace(tzinfo=timezone('Asia/Calcutta'))

    def resolve_products(self, info, **kwargs):
        return Order.objects.get(orderID=self['orderID']).products.values()

    def resolve_transaction(self, info, **kwargs):
        return Transaction.objects.values().get(id=self['transaction_id'])


class Query(object):
    myOrders = graphene.List(OrderObj)

    @login_required
    def resolve_myOrders(self, info, **kwargs):
        user = info.context.user
        return Order.objects.values().filter(user=user)
