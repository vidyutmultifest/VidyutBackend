import graphene
from datetime import datetime
from graphql_jwt.decorators import login_required
from django.utils import timezone

from products.models import Product, PromoCode
from payment.models import OrderProduct, Order
from registrations.models import EventRegistration

to_tz = timezone.get_default_timezone()


class InitiateOrderObj(graphene.ObjectType):
    orderID = graphene.String()


class ProductInput(graphene.InputObjectType):
    productID = graphene.String()
    qty = graphene.Int()


class ProductsInput(graphene.InputObjectType):
    products = graphene.List(ProductInput)


class InitiateOrder(graphene.Mutation):
    class Arguments:
        products = ProductsInput(required=True)
        promocode = graphene.String(required=False)
        regID = graphene.String(required=False)

    Output = InitiateOrderObj

    @login_required
    def mutate(self, info, products, promocode=None, regID=False):
        customer = info.context.user

        # CHECKING FOR PRIOR PURCHASE
        for product in products.products:
            p = Product.objects.get(productID=product.productID)

            # Checking for prior purchase of product by the user
            if p.restrictMultiplePurchases is False or Order.objects.filter(
                    products=p,
                    user=customer,
                    transaction__isPaid=True,
                    transaction__isProcessed=True
            ).count() < 1:
                pass
            else:
                # TODO: throw error as already purchased before
                return InitiateOrderObj(orderID=None)

        # Create Order with current timestamp
        timestamp = datetime.now().astimezone(to_tz)
        obj = Order.objects.create(user=customer, timestamp=timestamp)

        # Create Product - Order Mapping, along with Qty & Price data
        for product in products.products:
            p = Product.objects.get(productID=product.productID)
            OrderProduct.objects.create(product=p, order=obj, qty=product.qty, price=p.price)

        # APPLYING PROMOCODE
        if promocode is not None:
            try:
                pobj = PromoCode.objects.get(code=promocode)

                # Check if promocode is valid for user
                if (pobj.users is None | customer in pobj.users) & pobj.isActive:
                    obj.promoCode = pobj
                    obj.save()
                # TODO: throw error if promocode doesn't apply to the order

            except PromoCode.DoesNotExist:
                pass
                # TODO: throw error as it promocode doesnt exist

        # LINKING EVENT REGISTRATION
        if regID is not None:
            try:
                reg = EventRegistration.objects.get(regID=regID)
                if reg.event in obj.products.all():
                    reg.order = obj
                    reg.save()
            except EventRegistration.DoesNotExist:
                pass
                # TODO: throw error as event reg doesnt exist

        return InitiateOrderObj(orderID=obj.orderID)


class Mutation(object):
    initiateOrder = InitiateOrder.Field()
