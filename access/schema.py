import graphene
from graphql_jwt.decorators import login_required

from .models import *


class UserAccessObj(graphene.ObjectType):
    adminAccess = graphene.Boolean()
    canAcceptPayment = graphene.Boolean()
    canViewAllTransactions = graphene.Boolean()
    canIssueTickets = graphene.Boolean()
    canViewProfiles = graphene.Boolean()
    canViewRegistrations = graphene.Boolean()
    canGeneralCheckIn = graphene.Boolean()
    canCheckInUsers = graphene.Boolean()

    def resolve_canViewAllTransactions(self, info):
        return self.viewAllTransactions


class Query(graphene.ObjectType):
    myPermissions = graphene.Field(UserAccessObj)

    @login_required
    def resolve_myPermissions(self, info, **kwargs):
        user = info.context.user
        try:
            access = UserAccess.objects.get(user=user)
        except UserAccess.DoesNotExist:
            access = None
        return access
