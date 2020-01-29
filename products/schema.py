import json

import graphene
from graphql_jwt.decorators import login_required
from django.db.models import Q

from payment.models import Order
from .models import *
from events.schema import FormFieldObj, EventObj


class PromocodeObj(graphene.ObjectType):
    code = graphene.String()
    description = graphene.String()


class EventDetailObj(EventObj, graphene.ObjectType):
    formFields = graphene.List(FormFieldObj)

    def resolve_formFields(self, info):
        formFields = None
        if 'formFields' in self and self['formFields'] is not None and self['formFields'] is not '':
            formFields = json.loads(self['formFields'])
        return formFields


class ProductInfoObj(graphene.ObjectType):
    name = graphene.String()
    photo = graphene.String()
    price = graphene.Int()
    slug = graphene.String()
    type = graphene.String()
    isTotalRate = graphene.Boolean()
    details = graphene.Field(EventDetailObj)


class ProductObj(graphene.ObjectType):
    name = graphene.String()
    requireRegistration = graphene.Boolean()
    requireAdvancePayment = graphene.Boolean()
    restrictMultiplePurchases = graphene.Boolean()
    requireEventRegistration = graphene.Boolean()
    isAmritapurianOnly = graphene.Boolean()
    isOutsideOnly = graphene.Boolean()
    isSchoolOnly = graphene.Boolean()
    isGSTAccounted = graphene.Boolean()
    isFacultyOnly = graphene.Boolean()
    slots = graphene.Int()
    price = graphene.String()
    isAvailable = graphene.Boolean()
    showAgreementPage = graphene.Boolean()
    productID = graphene.String()
    product = graphene.Field(ProductInfoObj)

    def resolve_price(self, info):
        if self['isGSTAccounted']:
            # GST Amount = Original Cost – (Original Cost * (100 / (100 + GST% ) ) )
            price = self['price'] - (self['price'] - (self['price'] * (100 / (100 + 18))))
        else:
            price = self['price']
        return price

    def resolve_product(self, info):
        product = Product.objects.get(productID=self['productID']).product
        productType = type(product).__name__

        isTotalRate = True
        if product and hasattr(product, 'isTotalRate'):
            isTotalRate = product.isTotalRate

        photo = None
        if product.cover:
            photo = info.context.build_absolute_uri(product.cover.url)
        return {
            "name": product.name,
            "photo": photo,
            "price": product.fee,
            "isTotalRate": isTotalRate,
            "slug": product.slug,
            "type": productType,
            "details": type(product).objects.values().get(id=product.id)
        }


class FailingProductObj(graphene.ObjectType):
    name = graphene.String()
    sold = graphene.Int()

    def resolve_name(self, info):
        return self['product'].name


class Query(object):
    listPromocodes = graphene.List(PromocodeObj)
    listProducts = graphene.List(ProductObj)
    getProduct = graphene.Field(ProductObj, productID=graphene.String(required=True))
    listFailingProducts = graphene.List(FailingProductObj)

    @login_required
    def resolve_listProducts(self, info, **kwargs):
        return Product.objects.all()

    @login_required
    def resolve_listFailingProducts(self, info, **kwargs):
        list = []
        products = Product.objects.filter(Q(workshop__isnull=False) | Q(competition__isnull=False))
        for product in products:
            sold = Order.objects.filter(transaction__isPaid=True, products=product).count()
            if sold < 15:
                list.append({
                    "product": product,
                    "sold": sold
                })
        return list

#Q(competition__isnull=False)
    @login_required
    def resolve_listPromocodes(self, info, **kwargs):
        user = info.context.user
        return PromoCode.objects.values().filter(Q(users=user) | Q(users=None))

    @login_required
    def resolve_getPromocode(self, info, **kwargs):
        code = kwargs.get('code')
        return PromoCode.objects.values().filter(code=code)

    @login_required
    def resolve_getProduct(self, info, **kwargs):
        productID = kwargs.get('productID')
        return Product.objects.values().get(productID=productID)
