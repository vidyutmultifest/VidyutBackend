import uuid
import graphene
from graphql_jwt.decorators import login_required
from django.db.models import Q

from access.models import UserAccess
from participants.api.objects import ProfileObj
from participants.models import Profile
from registrations.models import EventRegistration

from framework.api.helper import APIException


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


class SingleProfileObj(ProfileObj, graphene.ObjectType):
    def resolve_hasEventsRegistered(self, info):
        count = EventRegistration.objects.filter((Q(user=self.user) | Q(team__members=self.user)) & (
                Q(order__transaction__isPaid=True) | Q(event__requireAdvancePayment=False))).count()
        return count > 0

    def resolve_photo(self, info):
        if self.photo and hasattr(self.photo, 'url'):
            return info.context.build_absolute_uri(self.photo.url)
        return None

    def resolve_idPhoto(self, info):
        if self.idPhoto and hasattr(self.idPhoto, 'url'):
            return info.context.build_absolute_uri(self.idPhoto.url)
        return None

    def resolve_firstName(self, info):
        return self.user.first_name

    def resolve_lastName(self, info):
        return self.user.last_name

    def resolve_email(self, info):
        return self.user.email

    def resolve_username(self, info):
        return self.user.username

    def resolve_isAmritian(self, info):
        isAmritian = True
        if self.user.email.split('@')[-1].find('amrita.edu') == -1:
            isAmritian = False
        return isAmritian

    def resolve_isAmritapurian(self, info):
        isAmritapurian = True
        if self.user.email.split('@')[-1].find('am.students.amrita.edu') == -1:
            isAmritapurian = False
        return isAmritapurian


class Query(object):
    isProfileComplete = graphene.Boolean()
    myProfile = graphene.Field(SingleProfileObj)
    getProfile = graphene.Field(SingleProfileObj, key=graphene.String(required=True))

    @login_required
    def resolve_isProfileComplete(self, info, **kwargs):
        user = info.context.user
        profile = Profile.objects.get(user=user)
        if profile.photo is None:
            return False
        # if profile.idPhoto is None:
        #     return False
        if profile.college is None and profile.rollNo is None:
            return False
        return True

    @login_required
    def resolve_myProfile(self, info, **kwargs):
        user = info.context.user
        return Profile.objects.get(user=user)

    @login_required
    def resolve_getProfile(self, info, **kwargs):
        user = info.context.user
        if UserAccess.objects.get(user=user).canViewProfiles:
            key = kwargs.get('key')
            if key is not None:
                try:
                    if is_valid_uuid(key):
                        return Profile.objects.get(vidyutHash=key)
                    return Profile.objects.get(
                        Q(vidyutID=key) | Q(user__username=key) | Q(user__email=key)
                    )
                except Profile.DoesNotExist:
                    raise APIException(
                        'Profile does not exist. Please enter a valid VidyutID / VidyutHash / Username / Email'
                    )
        raise APIException('You do not have the permission to view profiles of users')
