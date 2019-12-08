import graphene
from graphql_jwt.decorators import login_required
from .models import *

from .api.updateProfile import Mutation as updateProfileMutation
from .api.rekognitionAPI import Query as rekognitionQueries


class CreateCollegeObj(graphene.ObjectType):
    id = graphene.Int()


class AddCollege(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    Output = CreateCollegeObj

    @login_required
    def mutate(self, info, name=None):
        obj = College.objects.create(name=name)
        return CreateCollegeObj(id=obj.id)


class Mutation(updateProfileMutation, graphene.ObjectType):
    addCollege = AddCollege.Field()


class CollegeObj(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    location = graphene.String()


class ProfileObj(graphene.ObjectType):
    vidyutID = graphene.String()
    vidyutHash = graphene.String()
    username = graphene.String()
    firstName = graphene.String()
    lastName = graphene.String()
    email = graphene.String()
    phone = graphene.String()
    isAmritian = graphene.Boolean()
    isAmritapurian = graphene.Boolean()
    college = graphene.Field(CollegeObj)
    photo = graphene.String()
    idPhoto = graphene.String()
    location = graphene.String()
    graduationYear = graphene.String()
    rollNo = graphene.String()


class Query(rekognitionQueries, object):
    isProfileComplete = graphene.Boolean()
    myProfile = graphene.Field(ProfileObj)
    colleges = graphene.List(CollegeObj)
    # sendOTP = graphene.Boolean(phoneNo=graphene.String(required=True), message=graphene.String(required=True))

    @login_required
    def resolve_isProfileComplete(self, info, **kwargs):
        user = info.context.user
        profile = Profile.objects.get(user=user)
        if profile.photo is None:
            return False
        if profile.idPhoto is None:
            return False
        if profile.college is None and profile.rollNo is None:
            return False
        return True

    @login_required
    def resolve_myProfile(self, info, **kwargs):
        user = info.context.user
        profile = Profile.objects.get(user=user)

        isAmritian = True
        if user.email.split('@')[-1].find('amrita.edu') == -1:
            isAmritian = False

        isAmritapurian = True
        if user.email.split('@')[-1].find('am.students.amrita.edu') == -1:
            isAmritapurian = False

        photoUrl = None
        if profile.photo and hasattr(profile.photo, 'url') is not None:
            photoUrl = info.context.build_absolute_uri(profile.photo.url)
        #
        # idPhotoUrl = None
        # if profile.idPhoto and hasattr(profile.idPhoto, 'url') is not None:
        #     idPhotoUrl = info.context.build_absolute_uri(profile.idPhoto.url)

        return ProfileObj(
            firstName=user.first_name,
            lastName=user.last_name,
            email=user.email,
            isAmritian=isAmritian,
            isAmritapurian=isAmritapurian,
            username=user.username,
            vidyutID=profile.vidyutID,
            vidyutHash=profile.vidyutHash,
            phone=profile.phone,
            college=profile.college,
            photo=photoUrl,
            idPhoto=None,
            graduationYear=profile.graduationYear,
            rollNo=profile.rollNo
        )

    @staticmethod
    def resolve_colleges(self, info, **kwargs):
        return College.objects.values().all()


    #
    # @login_required
    # def resolve_sendOTP(self, info, **kwargs):
    #     phoneNo = kwargs.get('phoneNo')
    #     message = kwargs.get('message')
    #     client = boto3.client(
    #         "sns",
    #         'us-east-1',
    #         aws_access_key_id=AWS_ACCESS_KEY_ID,
    #         aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    #     )
    #     client.publish(
    #         PhoneNumber=phoneNo,
    #         Message=message
    #     )
    #     return True
