import uuid
import graphene
from graphql_jwt.decorators import login_required
from django.db.models import Q, Count

from access.models import UserAccess
from participants.api.objects import ProfileObj
from participants.models import Profile, College
from payment.models import Transaction
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


class TShirtSizeObj(graphene.ObjectType):
    s = graphene.Int()
    m = graphene.Int()
    l = graphene.Int()
    xl = graphene.Int()
    xxl = graphene.Int()
    unknown = graphene.Int()

    def resolve_s(self, info):
        return self.filter(shirtSize='S').count()

    def resolve_m(self, info):
        return self.filter(shirtSize='M').count()

    def resolve_l(self, info):
        return self.filter(shirtSize='L').count()

    def resolve_xl(self, info):
        return self.filter(shirtSize='XL').count()

    def resolve_xxl(self, info):
        return self.filter(shirtSize='XXL').count()

    def resolve_unknown(self, info):
        return self.count() - self.filter(
            Q(
                Q(shirtSize='XXL') |
                Q(shirtSize='XL') |
                Q(shirtSize='L') |
                Q(shirtSize='M') |
                Q(shirtSize='S')
            )
        ).count()


class CollegeStatObj(graphene.ObjectType):
    name = graphene.String()
    registeredUsers = graphene.Int()
    purchasedUsers = graphene.Int()

    def resolve_name(self, info):
        return College.objects.get(id=self[0]).name

    def resolve_registeredUsers(self, info):
        return self[1]

    def resolve_purchasedUsers(self, info):
        users = Transaction.objects.filter(isPaid=True).order_by('user').values_list('user', flat=True).distinct()
        return Profile.objects.filter(college=self[0], user__in=users).count()


class ProfileStatObj(graphene.ObjectType):
    profilesCount = graphene.Int()
    incompleteProfilesCount = graphene.Int()
    completeProfileCount = graphene.Int()
    tshirtSize = graphene.Field(TShirtSizeObj)
    colleges = graphene.List(CollegeStatObj)

    def resolve_profilesCount(self, info):
        return Profile.objects.all().count()

    def resolve_incompleteProfilesCount(self, info):
        return Profile.objects.filter(
            Q(photo__isnull=True) | Q(college__isnull=True) | Q(phone__isnull=True)
        ).count()

    def resolve_completeProfileCount(self, info):
        return Profile.objects.filter(
            Q(photo__isnull=False) & Q(college__isnull=False) & Q(phone__isnull=False)
        ).count()

    def resolve_colleges(self, info):
        colleges = Profile.objects.filter(college__isnull=False).order_by('college').values_list('college').annotate(rcount=Count('college')).distinct()
        return colleges

    def resolve_tshirtSize(self, info):
        users = Transaction.objects.filter(isPaid=True).order_by('user').values_list('user', flat=True).distinct()
        return Profile.objects.filter(user__in=users)


class Query(object):
    isProfileComplete = graphene.Boolean()
    myProfile = graphene.Field(SingleProfileObj)
    getProfile = graphene.Field(SingleProfileObj, key=graphene.String(required=True))
    listIncompleteProfiles = graphene.List(SingleProfileObj)
    getProfileStats = graphene.Field(ProfileStatObj)

    @login_required
    def resolve_isProfileComplete(self, info, **kwargs):
        user = info.context.user
        profile = Profile.objects.get(user=user)
        if profile.photo is None:
            return False
        # if profile.idPhoto is None:
        #     return False
        if profile.college is None:
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

    @login_required
    def resolve_listIncompleteProfiles(self, info):
        return Profile.objects.filter(
            Q(photo=None) | Q(college=None) | Q(phone=None)
        )[:10]

    @login_required
    def resolve_getProfileStats(self, info):
        return False
