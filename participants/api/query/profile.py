import uuid
import graphene
from django.core.mail import send_mail
from django.db.models.functions import Concat
from django.template.loader import get_template
from django.utils.html import strip_tags
from graphql_jwt.decorators import login_required
from django.db.models import Q, Count
from django.db.models import Value

from access.models import UserAccess
from framework.server_settings import EMAIL_HOST_USER
from participants.api.objects import ProfileObj
from participants.models import Profile, College
from payment.models import Transaction, Order
from registrations.models import EventRegistration

from framework.api.helper import APIException
from tickets.models import PhysicalTicket, CheckIn


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


class SingleProfileObj(ProfileObj, graphene.ObjectType):
    def resolve_hasEventsRegistered(self, info):
        count = EventRegistration.objects.filter((Q(user=self.user) | Q(team__members=self.user)) &
                                                 Q(order__transaction__isPaid=True)).count()
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

    # TODO fix logic later on - this was a temporary patch
    def resolve_isAmritapurian(self, info):
        isAmritapurian = True
        if self.user.email.split('@')[-1].find('amrita.edu') == -1:
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
        colleges = Profile.objects.filter(college__isnull=False).order_by('college').values_list('college').annotate(
            rcount=Count('college')).distinct()
        return colleges

    def resolve_tshirtSize(self, info):
        users = Transaction.objects.filter(isPaid=True).order_by('user').values_list('user', flat=True).distinct()
        return Profile.objects.filter(user__in=users)


class ProfileCompletionObj(graphene.ObjectType):
    status = graphene.Boolean()
    message = graphene.String()


class ProfileDetailedStats(SingleProfileObj, graphene.ObjectType):
    registrations = graphene.List(graphene.String)
    proshowTicket = graphene.String()
    profileCompletion = graphene.Field(ProfileCompletionObj)
    physicalTicket = graphene.String()
    hasCheckedIn = graphene.Boolean()

    def resolve_hasCheckedIn(self, info):
        return CheckIn.objects.filter(user=self.user, generalCheckIn=True).count() > 0

    def resolve_physicalTicket(self, info):
        try:
            return PhysicalTicket.objects.get(user=self.user).number
        except PhysicalTicket.DoesNotExist:
            return None

    def resolve_profileCompletion(self, info):
        profile = self
        isProfileComplete = True
        profilemsg = 'Profile Incomplete - '
        if not profile.photo or not hasattr(profile.photo, 'url'):
            isProfileComplete = False
            profilemsg += ' Selfie, '
        if not profile.idPhoto or not hasattr(profile.idPhoto, 'url'):
            isProfileComplete = False
            profilemsg += ' ID Card, '
        if profile.gender is None or len(profile.gender) < 1:
            isProfileComplete = False
            profilemsg += ' Gender, '
        if profile.phone is None or len(profile.phone) < 10:
            isProfileComplete = False
            profilemsg += ' Phone No., '
        if profile.college is None:
            isProfileComplete = False
            profilemsg += ' College Name, '
        profilemsg += ' to be updated'

        message = 'Profile Complete'
        status = True
        if isProfileComplete is False:
            status = False
            message = profilemsg
        return ProfileCompletionObj(status=status, message=message)

    def resolve_registrations(self, info):
        list = []
        q = EventRegistration.objects.filter(
            Q(Q(order__transaction__isPaid=True) | Q(event__price=0)) &
            Q(Q(team__members=self.user) | Q(user=self.user))
        )
        for r in q:
            type = ' / '
            if r.event.workshop is not None:
                type = 'Workshop'
            elif r.event.competition is not None:
                type = 'Competition'
            list.append(r.event.name + ' - ' + type)
        return list

    def resolve_proshowTicket(self, info):
        tickets = Order.objects.filter(
            Q(transaction__isPaid=True) &
            Q(user=self.user) &
            Q(products__name__contains='Revel')
        )
        if tickets.count() > 0:
            return tickets.first().products.first().name
        else:
            return 'No Ticket Found'


class Query(object):
    isProfileComplete = graphene.Boolean()
    myProfile = graphene.Field(SingleProfileObj)
    getProfile = graphene.Field(ProfileDetailedStats, key=graphene.String(required=True))
    listIncompleteProfiles = graphene.List(SingleProfileObj)
    # getProfileStats = graphene.Field(ProfileStatObj)
    # emailIncompleteInsiders = graphene.Boolean()

    # listEmails = graphene.String()
    #
    # @login_required
    # def resolve_listEmails(self, info, **kwargs):
    #     a = []
    #     list = Profile.objects.filter(
    #         user__email__contains='am.students.amrita.edu',
    #         user__transactionUser__isPaid=True
    #     ).values_list('user__email', flat=True)
    #     for l in list:
    #         a.append(l)
    #     return a

    # @login_required
    # def resolve_emailIncompleteInsiders(self, info, **kwargs):
    #     users = Profile.objects.filter(
    #         Q(user__email__contains='am.students.amrita.edu') &
    #         (Q(rollNo__isnull=True) | Q(college__isnull=True) | Q(shirtSize__isnull=True) |
    #          Q(phone__isnull=True)) & Q(user__transactionUser__isPaid=True)
    #     )
    #     i = 231
    #     for u in users[231:]:
    #         data = {
    #             "username": u.user.first_name + ' ' + u.user.last_name,
    #             "vidyutID": u.vidyutID
    #         }
    #         htmly = get_template('./emails/complete-profile.html')
    #         html_content = htmly.render(data)
    #         send_mail(
    #             'Please complete your Vidyut Profile',
    #             strip_tags(html_content),
    #             EMAIL_HOST_USER,
    #             [u.user.email],
    #             html_message=html_content,
    #             fail_silently=False,
    #         )
    #         print(i)
    #         i = i + 1
    #     return True

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

    def resolve_myProfile(self, info, **kwargs):
        user = info.context.user
        if user.id:
            return Profile.objects.get(user=user)
        return None

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
