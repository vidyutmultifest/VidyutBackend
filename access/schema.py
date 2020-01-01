import graphene
from graphql_jwt.decorators import login_required

from .models import *


class UserAccessObj(graphene.ObjectType):
    adminAccess = graphene.Boolean()
    canAcceptPayment = graphene.Boolean()
    canViewAllTransactions = graphene.Boolean()
    canIssueTickets = graphene.Boolean()
    canViewProfiles = graphene.Boolean()


class Query(graphene.ObjectType):
    myPermissions = graphene.Field(UserAccessObj)

    @login_required
    def resolve_myPermissions(self, info, **kwargs):
        user = info.context.user
        try:
            access = UserAccess.objects.values().get(user=user)
        except UserAccess.DoesNotExist:
            access = None
        return access
