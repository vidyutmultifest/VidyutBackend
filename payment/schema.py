import graphene
from datetime import datetime

from graphql_jwt.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.models import User
from access.models import UserAccess
from participants.models import Profile

from .models import Transaction, OrderProduct, Order
from products.models import Product

from .api.stats import Query as StatsQuery
from .api.order import Mutation as OrderMutations
from .api.transaction import Mutation as TransactionMutations
from .api.acrd import Query as ACRDQueries

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


class Mutation(OrderMutations, TransactionMutations, object):
    collectPayment = CollectPayment.Field()


class BuyerObj(graphene.ObjectType):
    firstName = graphene.String()
    lastName = graphene.String()
    vidyutID = graphene.String()
    photo = graphene.String()

    def resolve_photo(self, info):
        return ''


class IssuerObj(BuyerObj, graphene.ObjectType):
    location = graphene.String()
    device = graphene.String()


class OrderProductObj(graphene.ObjectType):
    name = graphene.String()
    price = graphene.Int()
    qty = graphene.Int()

    def resolve_name(self, info):
        return Product.objects.get(id=self['product_id']).name

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
    isPaid = graphene.Boolean()
    isPending = graphene.Boolean()
    isProcessed = graphene.Boolean()
    issuer = graphene.Field(IssuerObj)
    isOnline = graphene.Boolean()
    transactionData = graphene.String()

    def resolve_timestamp(self, info):
        return self['timestamp'].astimezone(to_tz)

    def resolve_issuer(self, info):
        if self['issuer_id']:
            user = User.objects.get(id=self['issuer_id'])
            vidyutID = Profile.objects.get(user=self['issuer_id']).vidyutID
            return IssuerObj(
                firstName=user.first_name,
                lastName=user.last_name,
                vidyutID=vidyutID,
                location=self['issuerLocation'],
                device=self['issuerDevice']
            )
        return None


class TransactionDetailObj(TransactionObj, graphene.ObjectType):
    products = graphene.List(OrderProductObj)
    user = graphene.Field(BuyerObj)

    def resolve_products(self, info):
        oid = Order.objects.filter(transaction_id=self['id']).first().id
        return OrderProduct.objects.values().filter(order_id=oid)

    def resolve_user(self, info):
        user = User.objects.get(id=self['user_id'])
        vidyutID = Profile.objects.get(user=self['user_id']).vidyutID
        return BuyerObj(
            firstName=user.first_name,
            lastName=user.last_name,
            vidyutID=vidyutID
        )


class OrderObj(graphene.ObjectType):
    orderID = graphene.String()
    timestamp = graphene.String()
    products = graphene.List(OrderProductObj)
    user = graphene.Field(BuyerObj)
    transaction = graphene.Field(TransactionObj)

    def resolve_timestamp(self, info):
        return self['timestamp'].astimezone(to_tz)

    def resolve_products(self, info, **kwargs):
        return OrderProduct.objects.values().filter(order_id=self['id'])

    def resolve_transaction(self, info, **kwargs):
        return Transaction.objects.values().get(id=self['transaction_id'])

    def resolve_user(self, info, **kwargs):
        user = User.objects.get(id=self['user_id'])
        vidyutID = Profile.objects.get(user=self['user_id'])
        return BuyerObj(firstName=user.first_name, lastName=user.last_name, vidyutID=vidyutID)


class TransactionStatusObj(graphene.ObjectType):
    isPaid = graphene.Boolean()
    isPending = graphene.Boolean()
    isProcessed = graphene.Boolean()
    issuer = graphene.Field(IssuerObj)
    timestamp = graphene.String()

    def resolve_isPaid(self, info):
        return self.isPaid

    def resolve_isPending(self, info):
        return self.isPending

    def resolve_isProcessed(self, info):
        return self.isProcessed

    def resolve_issuer(self, info):
        if self.issuer:
            vidyutID = Profile.objects.get(user=self.issuer).vidyutID
            return IssuerObj(
                firstName=self.issuer.first_name,
                lastName=self.issuer.last_name,
                vidyutID=vidyutID,
                location=self.issuerLocation,
                device=self.issuerDevice
            )
        return None

    def resolve_timestamp(self, info):
        return self.timestamp


class TransactionListObj(graphene.ObjectType):
    user = graphene.Field(BuyerObj)
    transactionID = graphene.String()
    isPaid = graphene.Boolean()
    isProcessed = graphene.Boolean()
    timestamp = graphene.String()
    fee = graphene.Int()
    manualIssue = graphene.Boolean()
    issuerLocation = graphene.String()
    issuerDevice = graphene.String()

    def resolve_user(self, info):
        return User.objects.get(user__id=self['user_id'])


class Query(ACRDQueries, StatsQuery, object):
    myOrders = graphene.List(OrderObj, limit=graphene.Int(required=False))
    getTransactionDetail = graphene.Field(TransactionDetailObj, transactionID=graphene.String())
    getTransactionsApproved = graphene.List(TransactionDetailObj)
    getAmountCollected = graphene.Int()
    getTransactionsApprovedCount = graphene.Int()
    getTransactionStatus = graphene.Field(TransactionStatusObj, transactionID=graphene.String())
    getTransactionsPendingCount = graphene.Int()
    getTransactionList = graphene.List(TransactionListObj)

    @login_required
    def resolve_myOrders(self, info, **kwargs):
        user = info.context.user
        limit = kwargs.get('limit')
        objs = Order.objects.values().filter(user=user).order_by("-timestamp")
        if limit is not None:
            return objs[:limit]
        else:
            return objs

    @login_required
    def resolve_getTransactionDetail(self, info, **kwargs):
        transactionID = kwargs.get('transactionID')
        user = info.context.user
        if UserAccess.objects.get(user=user).canAcceptPayment:
            tobj = Transaction.objects.get(transactionID=transactionID)
            if tobj.isPaid is False:
                tobj.issuer = user
                tobj.isPending = True
                tobj.isProcessed = False
                tobj.save()
            return Transaction.objects.values().get(transactionID=transactionID)

    @login_required
    def resolve_getTransactionsApproved(self, info, **kwargs):
        user = info.context.user
        if UserAccess.objects.get(user=user).canAcceptPayment:
            return Transaction.objects.values().filter(issuer=user, isPaid=True)

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

    @login_required
    def resolve_getTransactionStatus(self, info, **kwargs):
        user = info.context.user
        transactionID = kwargs.get('transactionID')
        tobj = Transaction.objects.get(transactionID=transactionID)
        if tobj.user == user:
            return tobj

    @login_required
    def resolve_getTransactionList(self, info, **kwargs):
        user = info.context.user
        if UserAccess.objects.get(user=user).viewAllTransactions:
            return Transaction.objects.values().all()
