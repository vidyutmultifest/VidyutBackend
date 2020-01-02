import graphene

from framework.api.helper import APIException
from participants.models import Profile
from payment.models import Order, OrderProduct


class BuyerObj(graphene.ObjectType):
    firstName = graphene.String()
    lastName = graphene.String()
    vidyutID = graphene.String()
    photo = graphene.String()


class IssuerObj(BuyerObj, graphene.ObjectType):
    location = graphene.String()
    device = graphene.String()


class OrderProductObj(graphene.ObjectType):
    name = graphene.String()
    price = graphene.Int()
    qty = graphene.Int()

    def resolve_name(self, info):
        return self.product.name


class TransactionStatusObj(graphene.ObjectType):
    isPaid = graphene.Boolean()
    isPending = graphene.Boolean()
    isProcessed = graphene.Boolean()
    issuer = graphene.Field(IssuerObj)
    timestamp = graphene.String()

    def resolve_issuer(self, info):
        if self.issuer is not None:
            try:
                profile = Profile.objects.get(user=self.issuer)
                photo = None
                # TODO doesnt seem to work
                if profile.photo and hasattr(profile.photo, "url"):
                    photo = info.context.build_absolute_uri(profile.photo.url)
                return IssuerObj(
                    firstName=self.issuer.first_name,
                    lastName=self.issuer.last_name,
                    location=self.issuerLocation,
                    device=self.issuerDevice,
                    vidyutID=profile.vidyutID,
                    photo=photo
                )
            except Profile.DoesNotExist:
                raise APIException('Issuer does not exist or has been deleted from db.')
        return None


class TransactionObj(TransactionStatusObj, graphene.ObjectType):
    transactionID = graphene.String()
    amount = graphene.String()
    isOnline = graphene.Boolean()
    transactionData = graphene.String()


class TransactionDetailObj(TransactionObj, graphene.ObjectType):
    products = graphene.List(OrderProductObj)
    user = graphene.Field(BuyerObj)

    def resolve_products(self, info):
        oid = Order.objects.filter(transaction_id=self.id).first().id
        return OrderProduct.objects.filter(order_id=oid)

    def resolve_user(self, info):
        profile = Profile.objects.get(user=self.user)
        photo = None
        if profile.photo and hasattr(profile.photo, "url"):
            photo = info.context.build_absolute_uri(profile.photo.url)
        return BuyerObj(
            firstName=self.user.first_name,
            lastName=self.user.last_name,
            vidyutID=profile.vidyutID,
            photo=photo
        )


class OrderObj(graphene.ObjectType):
    orderID = graphene.String()
    timestamp = graphene.String()
    products = graphene.List(OrderProductObj)
    user = graphene.Field(BuyerObj)
    transaction = graphene.Field(TransactionObj)

