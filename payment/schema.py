import graphene
from datetime import datetime

from django.core.mail import send_mail
from django.template.loader import get_template
from django.utils.html import strip_tags
from graphql_jwt.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.models import User
from access.models import UserAccess
from participants.models import Profile
from framework import settings


from .models import Transaction, OrderProduct, Order
from products.models import Product, PromoCode

to_tz = timezone.get_default_timezone()
from_email = settings.EMAIL_HOST_USER

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
        tObj = Transaction.objects.create(amount=fee, user=customer, timestamp=timestamp)
        oObj = Order.objects.create(user=customer, transaction=tObj, timestamp=timestamp)
        if promocode is not None:
            pobj = PromoCode.objects.get(code=promocode)
            if (pobj.users is None | customer in pobj.users) & pobj.isActive:
                oObj.promoCode = pobj
        for product in products.products:
            p = Product.objects.get(productID=product.productID)
            OrderProduct.objects.create(product=p, qty=product.qty, order=oObj)

        return InitiateOrderObj(transactionID=tObj.transactionID, orderID=oObj.orderID)


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
            order = Order.objects.get(transaction=t)
            if t.isPaid is False:
                timestamp = datetime.now().astimezone(to_tz)
                t.isProcessed = True
                if status == "paid":
                    t.isPaid = True
                    t.isPending = False
                    htmly = get_template('./emails/payment-confirmation.html')
                    d = {
                        'name': t.user.first_name,
                        'transactionID': str(t.transactionID),
                        'orderID': str(order.orderID),
                        'amount': str(t.amount),
                        'paymentMode': 'offline',
                        'issuer': issuer.first_name
                    }
                    html_content = htmly.render(d)
                    send_mail(
                        'Payment Confirmation for Order #' + str(order.orderID),
                        strip_tags(html_content),
                        from_email,
                        [t.user.email],
                        html_message=html_content,
                        fail_silently=False,
                    )
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


class Mutation(object):
    initiateOrder = InitiateOrder.Field()
    collectPayment = CollectPayment.Field()


class BuyerObj(graphene.ObjectType):
    firstName = graphene.String()
    lastName = graphene.String()
    vidyutID = graphene.String()


class IssuerObj(BuyerObj, graphene.ObjectType):
    location = graphene.String()
    device = graphene.String()


class OrderProductObj(graphene.ObjectType):
    name = graphene.String()
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
    isPaid = graphene.Boolean()
    isPending = graphene.Boolean()
    isProcessed = graphene.Boolean()

    def resolve_timestamp(self, info):
        return self['timestamp'].astimezone(to_tz)


class TransactionDetailObj(TransactionObj, graphene.ObjectType):
    products = graphene.List(OrderProductObj)
    user = graphene.Field(BuyerObj)
    issuer = graphene.Field(IssuerObj)

    def resolve_products(self, info):
        oid = Order.objects.filter(transaction_id=self['id']).first().id
        return OrderProduct.objects.values().filter(order_id=oid)

    def resolve_user(self, info):
        user = User.objects.get(id=self['user_id'])
        vidyutID = Profile.objects.get(user=self['user_id']).vidyutID
        return BuyerObj(firstName=user.first_name, lastName=user.last_name, vidyutID=vidyutID)

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


class OrderObj(graphene.ObjectType):
    orderID = graphene.String()
    timestamp = graphene.String()
    products = graphene.List(OrderProductObj)
    user = graphene.Field(BuyerObj)
    issuer = graphene.Field(IssuerObj)
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

    def resolve_issuer(self, info):
        user = User.objects.get(id=self['issuer_id'])
        vidyutID = Profile.objects.get(user=self['issuer_id']).vidyutID
        return IssuerObj(
            firstName=user.first_name,
            lastName=user.last_name,
            vidyutID=vidyutID,
            location=self['issuerLocation'],
            device=self['issuerDevice']
        )


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


class Query(object):
    myOrders = graphene.List(OrderObj)
    getTransactionDetail = graphene.Field(TransactionDetailObj, transactionID=graphene.String())
    getTransactionsApproved = graphene.List(TransactionDetailObj)
    getAmountCollected = graphene.Int()
    getTransactionsApprovedCount = graphene.Int()
    getTransactionStatus = graphene.Field(TransactionStatusObj, transactionID=graphene.String())

    @login_required
    def resolve_myOrders(self, info, **kwargs):
        user = info.context.user
        return Order.objects.values().filter(user=user).order_by("-timestamp")

    @login_required
    def resolve_getTransactionDetail(self, info, **kwargs):
        transactionID = kwargs.get('transactionID')
        user = info.context.user
        if UserAccess.objects.get(user=user).canAcceptPayment:
            tobj = Transaction.objects.get(transactionID=transactionID)
            tobj.issuer = user
            tobj.isPending = True
            tobj.isProcessed = False
            tobj.isPaid = False
            tobj.save()
            return Transaction.objects.values().get(transactionID=transactionID)

    @login_required
    def resolve_getTransactionsApproved(self, info, **kwargs):
        user = info.context.user
        if UserAccess.objects.get(user=user).canAcceptPayment:
            return Transaction.objects.values().filter(issuer=user)

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
    def resolve_getTransactionStatus(self, info, **kwargs):
        user = info.context.user
        transactionID = kwargs.get('transactionID')
        tobj = Transaction.objects.get(transactionID=transactionID)
        if tobj.user == user:
            return tobj
