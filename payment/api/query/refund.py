import graphene
from graphql_jwt.decorators import login_required

from participants.models import Profile
from payment.models import OrderProduct


class RefundObj(graphene.ObjectType):
    product = graphene.String()
    amount = graphene.Int()
    isOnline = graphene.Boolean()
    hasRefunded = graphene.Boolean()
    userName = graphene.String()
    transaction = graphene.String()


class Query(object):
    getRefunds = graphene.Field(RefundObj, hash=graphene.String())

    @login_required
    def resolve_getRefunds(self, info, **kwargs):
        hash = kwargs.get('hash')
        try:
            user = Profile.objects.get(vidyutHash=hash).user
            try:
                op = OrderProduct.objects.filter(
                    order__user=user,
                    order__transaction__isPaid=True,
                    order__products__name__contains='Revel'
                )
                if op.count() == 1:
                    return RefundObj(
                        userName=user.first_name + ' ' + user.last_name,
                        product=op.first().order.products.first().name,
                        amount=op.first().order.transaction.amount * 0.5,
                        isOnline=op.first().order.transaction.isOnline,
                        transaction=op.first().order.transaction.transactionID
                    )
            except OrderProduct.DoesNotExist:
                return None
        except Profile.DoesNotExist:
            return None
