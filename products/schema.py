import graphene
from graphql_jwt.decorators import login_required
from django.db.models import Q

from .models import *


class PromocodeObj(graphene.ObjectType):
    code = graphene.String()
    description = graphene.String()


class ProductObj(graphene.ObjectType):
    name = graphene.String()
    description = graphene.String()
    price = graphene.Int()


class Query(object):
    getProduct = graphene.Field(ProductObj, id=graphene.Int())
    listProducts = graphene.List(ProductObj)
    listPromocodes = graphene.List(PromocodeObj)
    # verifyPromocode = graphene.Field()

    def resolve_getProduct(self, info, **kwargs):
        product_id = kwargs.get('id')
        return Product.objects.values().get(id=product_id)

    def resolve_listProducts(self, info, **kwargs):
        return Product.objects.values().all()

    @login_required
    def resolve_listPromocodes(self, info, **kwargs):
        user = info.context.user
        return PromoCode.objects.values().filter(Q(users=user) | Q(users=None))
