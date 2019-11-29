import graphene

from .models import *
from graphql_jwt.decorators import login_required
from django.utils import timezone
from datetime import datetime

from access.models import UserAccess

to_tz = timezone.get_default_timezone()


class InitiateOrderObj(graphene.ObjectType):
    transactionID = graphene.String()
    orderID = graphene.String()


class OrderStatusObj(graphene.ObjectType):
    status = graphene.Boolean()


class ProductInput(graphene.InputObjectType):
    productID = graphene.String()
    qty = graphene.Int()


class ProductsInput(graphene.InputObjectType):
    products = graphene.List(ProductInput)


class InitiateOrder(graphene.Mutation):
    class Arguments:
        products = ProductsInput(required=True)
        promocode = graphene.String(required=False)

    Output = InitiateOrderObj

    @login_required
    def mutate(self, info, products, promocode=None):
        fee = 0
        customer = info.context.user
        for product in products.products:
            fee = fee + Product.objects.get(productID=product.productID).product.fee

        timestamp = datetime.now().astimezone(to_tz)
        tObj = Transaction.objects.create(amount=fee, user=customer, manualIssue=False, isSuccessful=False, timestamp=timestamp)
        oObj = Order.objects.create(user=customer, transaction=tObj, timestamp=timestamp)
        for product in products.products:
            p = Product.objects.get(productID=product.productID)
            OrderProduct.objects.create(product=p, qty=product.qty, order=oObj)

        return InitiateOrderObj(transactionID=tObj.transactionID, orderID=oObj.orderID)


class CollectPayment(graphene.Mutation):
    class Arguments:
        transactionID = graphene.String(required=True)

    Output = OrderStatusObj

    @login_required
    def mutate(self, info, transactionID):
        issuer = info.context.user
        if UserAccess.objects.get(user=issuer).canAcceptPayment:
            t = Transaction.objects.get(transactionID=transactionID)
            if t.isSuccessful is False:
                timestamp = datetime.now().astimezone(to_tz)
                t.isSuccessful = True
                t.manualIssue = True
                t.issuer = issuer
                t.timestamp = timestamp
                t.save()
                return {"status": True}
        return {"status": False}


class Mutation(object):
    initiateOrder = InitiateOrder.Field()
    collectPayment = CollectPayment.Field()


class OrderProductObj(graphene.ObjectType):
    name = graphene.String()
    photo = graphene.String()
    price = graphene.Int()
    qty = graphene.Int()

    def resolve_name(self, info):
        return Product.objects.get(id=self['product_id']).product.name

    def resolve_photo(self, info):
        cover = Product.objects.get(id=self['product_id']).product.cover
        url = None
        if cover is not '':
            url = info.context.build_absolute_uri(cover.url)
        return url

    def resolve_price(self, info):
        return Product.objects.get(id=self['product_id']).product.fee

    def resolve_qty(self, info):
        return self['qty']


class TransactionObj(graphene.ObjectType):
    transactionID = graphene.String()
    timestamp = graphene.String()
    amount = graphene.String()
    isSuccessful = graphene.Boolean()

    def resolve_timestamp(self, info):
        return self['timestamp'].astimezone(to_tz)


class OrderObj(graphene.ObjectType):
    orderID = graphene.String()
    timestamp = graphene.String()
    products = graphene.List(OrderProductObj)
    transaction = graphene.Field(TransactionObj)

    def resolve_timestamp(self, info):
        return self['timestamp'].astimezone(to_tz)

    def resolve_products(self, info, **kwargs):
        return OrderProduct.objects.values().filter(order_id=self['id'])

    def resolve_transaction(self, info, **kwargs):
        return Transaction.objects.values().get(id=self['transaction_id'])


class Query(object):
    myOrders = graphene.List(OrderObj)
    getTransactionDetail = graphene.Field(TransactionObj, transactionID=graphene.String())

    @login_required
    def resolve_myOrders(self, info, **kwargs):
        user = info.context.user
        return Order.objects.values().filter(user=user)

    @login_required
    def resolve_getTransactionDetail(self, info, **kwargs):
        transactionID = kwargs.get('transactionID')
        user = info.context.user
        if UserAccess.objects.get(user=user).canAcceptPayment:
            return Transaction.objects.values().get(transactionID=transactionID)
