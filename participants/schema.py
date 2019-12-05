import graphene
from graphql_jwt.decorators import login_required
from .models import *
import boto3
from framework.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


class UpdateProfileObj(graphene.ObjectType):
    status = graphene.Boolean()


class ProfileDetailsObj(graphene.InputObjectType):
    firstName = graphene.String(required=False)
    lastName = graphene.String(required=False)
    rollNo = graphene.String(required=False)
    phone = graphene.String(required=False)
    location = graphene.String(required=False)


class UpdateProfile(graphene.Mutation):
    class Arguments:
        details = ProfileDetailsObj(required=False)

    Output = UpdateProfileObj

    @login_required
    def mutate(self, info, details=None):
        user = info.context.user
        profile = Profile.objects.get(user=user)

        if info.context.FILES is not None:
            if "profilePhoto" in info.context.FILES:
                profilePhoto = info.context.FILES['profilePhoto']
                if profilePhoto is not None:
                    profile.photo = profilePhoto
            if "profileCollegeID" in info.context.FILES:
                profileCollegeID = info.context.FILES['profileCollegeID']
                if profileCollegeID is not None:
                    profile.idPhoto = profileCollegeID
        if details is not None:
            if details.firstName is not None:
                user.first_name = details.firstName
            if details.lastName is not None:
                user.last_name = details.lastName
            if details.rollNo is not None:
                profile.rollNo = details.rollNo
            if details.phone is not None:
                profile.phone = details.phone
            if details.location is not None:
                profile.location = details.location
            user.save()
        profile.save()

        return UpdateProfileObj(status=True)


class Mutation(graphene.ObjectType):
    updateProfile = UpdateProfile.Field()


class CollegeObj(graphene.ObjectType):
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


class RekognitionObj(graphene.ObjectType):
    jsonData = graphene.String()


class Query(object):
    isProfileComplete = graphene.Boolean()
    myProfile = graphene.Field(ProfileObj)
    colleges = graphene.List(CollegeObj)
    detectFace = graphene.Field(RekognitionObj)
    detectText = graphene.Field(RekognitionObj)
    sendOTP = graphene.Boolean(phoneNo=graphene.String(required=True), message=graphene.String(required=True))

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

    @login_required
    def resolve_detectFace(self, info, **kwargs):
        rekognition = boto3.client(
            "rekognition",
            'ap-south-1',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        photo = info.context.FILES['photo']
        return RekognitionObj(jsonData=str(rekognition.detect_faces(
            Image={
                "Bytes": photo.read()
            },
            Attributes=["DEFAULT"],
        )))

    @login_required
    def resolve_detectText(self, info, **kwargs):
        rekognition = boto3.client(
            "rekognition",
            'ap-south-1',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        photo = info.context.FILES['photo']
        return RekognitionObj(jsonData=str(rekognition.detect_text(
            Image={
                "Bytes": photo.read()
            }
        )))

    @login_required
    def resolve_sendOTP(self, info, **kwargs):
        phoneNo = kwargs.get('phoneNo')
        message = kwargs.get('message')
        client = boto3.client(
            "sns",
            'us-east-1',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        client.publish(
            PhoneNumber=phoneNo,
            Message=message
        )
        return True
