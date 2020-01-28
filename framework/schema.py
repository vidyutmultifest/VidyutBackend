import secrets
import string

import graphene
import graphql_jwt
import graphql_social_auth
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import get_template
from django.utils.html import strip_tags
from graphql_jwt.decorators import login_required

from framework.settings import EMAIL_HOST_USER

from access.schema import Query as AccessQueries
from events.schema import Query as EventQueries
from participants.models import Profile, Team
from participants.schema import Query as ParticipantQueries, Mutation as ParticipantMutation
from payment.models import Order, Transaction
from products.schema import Query as ProductQueries
from payment.schema import Query as PaymentQueries, Mutation as PaymentMutations
from registrations.models import EventRegistration
from tickets.schema import Query as TicketQueries, Mutation as TicketMutations
from registrations.schema import Mutation as RegMutations, Query as RegQueries
from social.schema import Query as SocialQueries
from forum.schema import Query as ForumQueries
from crew.schema import Query as CrewQueries
from framework.settings import *


class StatusObj(graphene.ObjectType):
    onlinePayment = graphene.Boolean()
    offlinePayment = graphene.Boolean()
    promocodes = graphene.Boolean()
    referrals = graphene.Boolean()
    googleSignIn = graphene.Boolean()
    facebookSignIn = graphene.Boolean()
    updatePhoto = graphene.Boolean()
    enableTicketing = graphene.Boolean()
    enableWorkshopRegistration = graphene.Boolean()
    enableCompetitionRegistration = graphene.Boolean()
    enableMerchandiseShopping = graphene.Boolean()
    enableCheckIn = graphene.Boolean()
    pushNotification = graphene.String()


class Query(
    AccessQueries,
    EventQueries,
    ParticipantQueries,
    ProductQueries,
    PaymentQueries,
    TicketQueries,
    RegQueries,
    SocialQueries,
    ForumQueries,
    CrewQueries,
    graphene.ObjectType
):
    status = graphene.Field(StatusObj)
    emailPassword = graphene.Boolean(email=graphene.String())
    transfer = graphene.Boolean(oldEmail=graphene.String(), newEmail=graphene.String())

    @login_required
    def resolve_transfer(self, info, **kwargs):
        if info.context.user.is_superuser():
            oldEmail = kwargs.get('oldEmail')
            newEmail = kwargs.get('newEmail')
            oldUser = User.objects.get(email=oldEmail)
            newUser = User.objects.get(email=newEmail)

            # transfer orders
            oldOrders = Order.objects.filter(user=oldUser)
            for o in oldOrders:
                o.orders.user = newUser
                o.save()

            # transfer transactions
            oldTransactions = Transaction.objects.filter(user=oldUser)
            for o in oldTransactions:
                o.user = newUser
                o.save()

            # transfer registrations
            eventRegs = EventRegistration.objects.filter(user=oldUser)
            for e in eventRegs:
                e.user = newUser
                e.save()

            # transfer team registrations
            teams = Team.objects.filter(members=oldUser)
            for t in teams:
                if t.leader == oldUser:
                    t.leader = newUser
                t.members.remove(oldUser)
                t.members.add(newUser)
                t.save()

            return True
        return False


    @staticmethod
    def resolve_emailPassword(self, info, **kwargs):
        email = kwargs.get('email')
        try:
            user = User.objects.get(email=email)
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(10))
            user.set_password(password)
            user.save()

            data = {
               "name": user.first_name + ' ' + user.last_name,
               "username": user.username,
               "password": password
            }
            htmly = get_template('./emails/password-reset.html')
            html_content = htmly.render(data)
            send_mail(
                'Your password for Vidyut 2020',
                strip_tags(html_content),
                EMAIL_HOST_USER,
                [email],
                html_message=html_content,
                fail_silently=False,
            )
            return True
        except User.DoesNotExist:
            username = email.split('@')[0]
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(10))
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.set_password(password)
            user.first_name = username
            user.save()
            data = {
                "name": user.first_name + ' ' + user.last_name,
                "username": user.username,
                "password": password
            }
            htmly = get_template('./emails/password-reset.html')
            html_content = htmly.render(data)
            send_mail(
                'Your Account for Vidyut 2020',
                strip_tags(html_content),
                EMAIL_HOST_USER,
                [email],
                html_message=html_content,
                fail_silently=False,
            )
            return True

    @staticmethod
    def resolve_status(self, info, **kwargs):
        return StatusObj(
            onlinePayment=ONLINE_PAYMENT_STATUS,
            offlinePayment=OFFLINE_PAYMENT_STATUS,
            promocodes=PROMOCODES_STATUS,
            referrals=REFERRAL_STATUS,
            googleSignIn=GOOGLE_SIGNIN_STATUS,
            facebookSignIn=FACEBOOK_SIGNIN_STATUS,
            updatePhoto=UPDATE_PHOTO_STATUS,
            enableTicketing=ENABLE_TICKETING,
            enableWorkshopRegistration=ENABLE_WORKSHOP_REGISTRATION,
            enableCompetitionRegistration=ENABLE_COMPETITION_REGISTRATION,
            enableMerchandiseShopping=ENABLE_MERCHANDISE_SHOPPING,
            enableCheckIn=ENABLE_CHECKIN,
            pushNotification=PUSH_NOTIFICATION
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


class Mutation(
    ParticipantMutation,
    PaymentMutations,
    TicketMutations,
    RegMutations,
    graphene.ObjectType
):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    social_auth = SocialAuth.Field()


schema = graphene.Schema(mutation=Mutation, query=Query)
