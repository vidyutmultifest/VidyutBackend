import json

import graphene
from graphql_jwt.decorators import login_required
from django.db.models import Q
from .models import *
from events.schema import FormFieldObj, EventObj


class PromocodeObj(graphene.ObjectType):
    code = graphene.String()
    description = graphene.String()


class EventDetailObj(EventObj, graphene.ObjectType):
    formFields = graphene.List(FormFieldObj)

    def resolve_formFields(self, info):
        formFields = None
        if self['formFields'] is not None and self['formFields'] is not '':
            formFields = json.loads(self['formFields'])
        return formFields


class ProductInfoObj(graphene.ObjectType):
    name = graphene.String()
    photo = graphene.String()
    price = graphene.Int()
    slug = graphene.String()
    type = graphene.String()
    details = graphene.Field(EventDetailObj)


class ProductObj(graphene.ObjectType):
    isAvailable = graphene.String()
    productID = graphene.String()
    product = graphene.Field(ProductInfoObj)

    def resolve_product(self, info):
        product = Product.objects.get(productID=self['productID']).product
        productType = type(product).__name__

        photo = None
        if product.cover:
            photo = info.context.build_absolute_uri(product.cover.url)
        return {
            "name": product.name,
            "photo": photo,
            "price": product.fee,
            "slug": product.slug,
            "type": productType,
            "details": type(product).objects.values().get(id=product.id)
        }


class Query(object):
    listPromocodes = graphene.List(PromocodeObj)
    getProduct = graphene.Field(ProductObj, productID=graphene.String(required=True))

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
