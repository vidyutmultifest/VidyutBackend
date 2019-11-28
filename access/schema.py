import graphene
from graphql_jwt.decorators import login_required

from .models import *


class UserAccessObj(graphene.ObjectType):
    adminAccess = graphene.Boolean()
    canAcceptPayment = graphene.Boolean()


class Query(graphene.ObjectType):
    myPermissions = graphene.Field(UserAccessObj)

    @login_required
    def resolve_myPermissions(self, info, **kwargs):
        user = info.context.user
        return UserAccess.objects.values().get(user=user)
