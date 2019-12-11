import graphene
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db.models import Sum
from graphql_jwt.decorators import login_required

from access.models import UserAccess
from payment.models import Transaction, Order, OrderProduct
from products.models import Product


class BasicTransactionObj(graphene.ObjectType):
    transactionID = graphene.String()
    username = graphene.String()
    orderID = graphene.String()

    def resolve_orderID(self, info):
        return Order.objects.get(transaction__transactionID=self['transactionID']).orderID


class DeviceObj(graphene.ObjectType):
    browser = graphene.String()
    os = graphene.String()
    vendor = graphene.String()
    model = graphene.String()


class LocationObj(graphene.ObjectType):
    latitude = graphene.String()
    longitude = graphene.String()


class IssuerStatObj(graphene.ObjectType):
    name = graphene.String()
    totalApproved = graphene.Int()
    totalPending = graphene.Int()
    totalHandled = graphene.Int()
    amount = graphene.Int()
    devices = graphene.List(DeviceObj)
    location = graphene.List(LocationObj)

    def resolve_name(self, info):
        issuer = self['issuer']
        return issuer.first_name + ' ' + issuer.last_name

    def resolve_totalApproved(self, info):
        return self['transactions'].filter(isPaid=True).count()

    def resolve_totalHandled(self, info):
        return self['transactions'].filter(isProccessed=True).count()

    def resolve_totalPending(self, info):
        return self['transactions'].filter(isPending=True).count()

    def resolve_amount(self, info):
        return self['transactions'].filter(isPaid=True).aggregate(Sum('amount'))['amount__sum']

    def resolve_devices(self, info):
        devices = self['transactions'].order_by().values_list('issuerDevice', flat=True).distinct()
        list = []
        for device in devices:
            if device is not None:
                list.append({
                    "browser":  device.split(',')[0],
                    "os": device.split(',')[1],
                    "vendor": device.split(',')[2],
                    "model": device.split(',')[3],
                })
            else:
                list.append({})
        return list

    def resolve_location(self, info):
        locations = self['transactions'].order_by().values_list('issuerLocation', flat=True).distinct()
        list = []
        latlonglist = []
        for location in locations:
            if location is not None:
                lat = round(float(location.split(', ')[0]), 3)
                long = round(float(location.split(', ')[1]), 3)
                latlong = [lat, long]
                if latlong not in latlonglist:
                    latlonglist.append(latlong)
                    list.append({
                        "latitude": lat,
                        "longitude": long,
                    })
            else:
                list.append({})
        return list


class ProductStatObj(graphene.ObjectType):
    name = graphene.String()
    productID = graphene.String()
    qtySold = graphene.Int()
    totalAmount = graphene.Int()
    transactions = graphene.List(BasicTransactionObj)

    def resolve_name(self, info):
        return Product.objects.get(productID=self['productID']).name

    def resolve_totalAmount(self, info):
        fee = Product.objects.get(productID=self['productID']).product.fee
        qty = self['transactions'].filter(isPaid=True).count()
        return fee * qty

    def resolve_transactions(self, info):
        plist = []
        for trans in self['transactions'].filter(isPaid=True):
            plist.append({
                "transactionID": trans.transactionID,
                "username": trans.user.username
            })
        return plist


class DailyTransactionStatObject(graphene.ObjectType):
    totalAmount = graphene.Int()
    date = graphene.Date()
    totalTransactions = graphene.Int()
    totalSuccessfulTransactions = graphene.Int()
    totalPendingTransactions = graphene.Int()
    productStats = graphene.List(
        ProductStatObj,
        productID=graphene.String(),
    )
    issuerStats = graphene.List(IssuerStatObj)

    def resolve_date(self, info):
        return self

    def resolve_totalAmount(self, info):
        return Transaction.objects.filter(timestamp__date=self, isPaid=True, isProcessed=True).aggregate(Sum('amount'))['amount__sum']

    def resolve_totalTransactions(self, info):
        return Transaction.objects.filter(timestamp__date=self).count()

    def resolve_totalSuccessfulTransactions(self, info):
        return Transaction.objects.filter(timestamp__date=self, isPaid=True, isProcessed=True).count()

    def resolve_totalPendingTransactions(self, info):
        return Transaction.objects.filter(timestamp__date=self, isPending=True, isProcessed=True).count()

    def resolve_productStats(self, info, **kwargs):
        plist = []
        productQueried = kwargs.get('productID')
        products = Transaction.objects.filter(timestamp__date=self, isPaid=True).order_by().values_list('order__products__productID', flat=True).distinct()
        if productQueried is None:
            for productID in products:
                product = Product.objects.get(productID=productID)
                trans = Transaction.objects.filter(timestamp__date=self, isPaid=True, order__products=product)
                qty = 0
                for tran in trans:
                    order = Order.objects.get(transaction=tran)
                    qty = qty + OrderProduct.objects.get(order=order).qty
                plist.append({
                    "qtySold": qty,
                    "transactions": trans,
                    "productID": productID
                })
        else:
            product = Product.objects.get(productID=productQueried)
            trans = Transaction.objects.filter(timestamp__date=self, isPaid=True, order__products=product)
            qty = 0
            for tran in trans:
                order = Order.objects.get(transaction=tran)
                qty = qty + OrderProduct.objects.get(order=order).qty
            plist.append({
                "qtySold": qty,
                "transactions": trans,
                "productID": product.productID
            })
        return plist

    def resolve_issuerStats(self, info):
        ilist = []
        issuers = Transaction.objects.filter(timestamp__date=self, isPaid=True).order_by().values_list('issuer', flat=True).distinct()
        for issuer in issuers:
            issuer = User.objects.get(id=issuer)
            transactions = Transaction.objects.filter(timestamp__date=self, issuer=issuer)
            ilist.append({
                "issuer": issuer,
                "transactions": transactions
            })
        return ilist


class TransactionStatObject(graphene.ObjectType):
    totalAmount = graphene.Int()
    productStats = graphene.List(ProductStatObj, productID=graphene.String())
    issuerStats = graphene.List(IssuerStatObj)
    dailyStats = graphene.List(
        DailyTransactionStatObject,
        date=graphene.Date(),
        startDate=graphene.Date(),
        endDate=graphene.Date()
    )

    def resolve_totalAmount(self, info):
        return Transaction.objects.filter(isPaid=True, isProcessed=True).aggregate(Sum('amount'))['amount__sum']

    def resolve_productStats(self, info, **kwargs):
        plist = []
        productQueried = kwargs.get('productID')
        products = Transaction.objects.filter(isPaid=True).order_by().values_list('order__products__productID', flat=True).distinct()
        if productQueried is None:
            for product in products:
                trans = Transaction.objects.filter(isPaid=True, order__products=product)
                qty = 0
                for tran in trans:
                    order = Order.objects.get(transaction=tran)
                    qty = qty + OrderProduct.objects.get(order=order).qty
                plist.append({
                    "qtySold": qty,
                    "transactions": trans,
                    "productID": product
                })
        else:
            product = Product.objects.get(productID=productQueried)
            trans = Transaction.objects.filter(isPaid=True, order__products=product)
            qty = 0
            for tran in trans:
                order = Order.objects.get(transaction=tran)
                qty = qty + OrderProduct.objects.get(order=order).qty
            plist.append({
                "qtySold": qty,
                "transactions": trans,
                "productID": product.productID
            })
        return plist

    def resolve_dailyStats(self, info, **kwargs):
        date = kwargs.get('date')
        startDate = kwargs.get('startDate')
        endDate = kwargs.get('endDate')
        dates = []
        if startDate is not None and endDate is not None:
            delta = endDate - startDate
            for i in range(delta.days + 1):
                day = startDate + timedelta(days=i)
                dates.append(day)
            dates.reverse()
        elif date is None:
            dates.append(datetime.now())
        elif date is not None:
            dates.append(date)
        return dates

    def resolve_issuerStats(self, info):
        ilist = []
        issuers = Transaction.objects.filter(isPaid=True).order_by().values_list('issuer', flat=True).distinct()
        for issuer in issuers:
            issuer = User.objects.get(id=issuer)
            transactions = Transaction.objects.filter(issuer=issuer)
            ilist.append({
                "issuer": issuer,
                "transactions": transactions
            })
        return ilist


class Query(object):
    getTransactionStats = graphene.Field(
        TransactionStatObject,
        date=graphene.Date(),
    )

    @login_required
    def resolve_getTransactionStats(self, info, **kwargs):
        user = info.context.user
        if UserAccess.objects.get(user=user).viewAllTransactions or user.is_superuser:
            return True
