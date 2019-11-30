import graphene
import graphql_jwt
import graphql_social_auth

from access.schema import Query as AccessQueries
from events.schema import Query as EventQueries
from participants.schema import Query as ParticipantQueries, Mutation as ParticipantMutation
from products.schema import Query as ProductQueries
from payment.schema import Query as PaymentQueries, Mutation as PaymentMutations

from framework.settings import *


class StatusObj(graphene.ObjectType):
    onlinePayment = graphene.Boolean()
    offlinePayment = graphene.Boolean()
    promocodes = graphene.Boolean()
    referrals = graphene.Boolean()
    googleSignIn = graphene.Boolean()
    updatePhoto = graphene.Boolean()


class Query(AccessQueries, EventQueries, ParticipantQueries, ProductQueries, PaymentQueries, graphene.ObjectType):
    status = graphene.Field(StatusObj)

    @staticmethod
    def resolve_status(self, info, **kwargs):
        return StatusObj(
            onlinePayment=ONLINE_PAYMENT_STATUS,
            offlinePayment=OFFLINE_PAYMENT_STATUS,
            promocodes=PROMOCODES_STATUS,
            referrals=REFERRAL_STATUS,
            googleSignIn=GOOGLE_SIGNIN_STATUS,
            updatePhoto=UPDATE_PHOTO_STATUS
        )


class UserType(graphene.ObjectType):
    username = graphene.Field(graphene.String)


class SocialAuth(graphql_social_auth.SocialAuthJWT):
    user = graphene.Field(UserType)
    token = graphene.String()

    @classmethod
    def resolve(cls, root, info, social, **kwargs):
        try:
            from graphql_jwt.shortcuts import get_token, get_refresh_token, create_refresh_token
        except ImportError:
            raise ImportError(
                'django-graphql-jwt not installed.\n'
                'Use `pip install \'django-graphql-social-auth[jwt]\'`.')
        return cls(user=social.user, token=get_token(social.user))


class Mutation(ParticipantMutation, PaymentMutations, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    social_auth = SocialAuth.Field()


schema = graphene.Schema(mutation=Mutation, query=Query)
