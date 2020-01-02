import graphene
from graphql_jwt.decorators import login_required
from django.utils import timezone

from participants.models import Profile
from payment.api.objects import OrderObj, BuyerObj
from payment.models import OrderProduct, Order

to_tz = timezone.get_default_timezone()


class MultipleOrderObj(OrderObj, graphene.ObjectType):
    def resolve_timestamp(self, info):
        return self.timestamp.astimezone(to_tz)

    def resolve_products(self, info, **kwargs):
        return OrderProduct.objects.filter(order=self)

    def resolve_transaction(self, info, **kwargs):
        return self.transaction

    def resolve_user(self, info, **kwargs):
        vidyutID = Profile.objects.get(user=self.user)
        return BuyerObj(firstName=self.user.first_name, lastName=self.user.last_name, vidyutID=vidyutID)


class Query(graphene.ObjectType):
    myOrders = graphene.List(MultipleOrderObj, limit=graphene.Int(required=False))

    @login_required
    def resolve_myOrders(self, info, **kwargs):
        user = info.context.user
        limit = kwargs.get('limit')
        objs = Order.objects.filter(user=user).order_by("-timestamp")
        orders = []
        for o in objs:
            orders.append(o)
        if limit is not None:
            return orders[:limit]
        else:
            return orders
