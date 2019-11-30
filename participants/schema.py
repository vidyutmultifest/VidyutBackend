import graphene
from graphql_jwt.decorators import login_required
from .models import *
import cv2
import os

FACE_DETECTOR_PATH = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


class SelfieUploadObj(graphene.ObjectType):
    status = graphene.Boolean()


class UploadSelfie(graphene.Mutation):
    Output = SelfieUploadObj

    @login_required
    def mutate(self, info):
        user = info.context.user
        file = info.context.FILES['imageFile']
        profile = Profile.objects.get(user=user)
        profile.photo = file
        profile.save()

        return SelfieUploadObj(status=True)


class Mutation(graphene.ObjectType):
    uploadSelfie = UploadSelfie.Field()


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
    location = graphene.String()
    graduationYear = graphene.String()


class Query(object):
    myProfile = graphene.Field(ProfileObj)
    colleges = graphene.List(CollegeObj)
    isValidFace = graphene.Boolean()

    @login_required
    def resolve_myProfile(self, info, **kwargs):
        user = info.context.user
        profile = Profile.objects.get(user=user)
        user = profile.user

        isAmritian = True
        if user.email.split('@')[-1].find('amrita.edu') == -1:
            isAmritian = False

        isAmritapurian = True
        if user.email.split('@')[-1].find('am.students.amrita.edu') == -1:
            isAmritapurian = False

        photoUrl = None
        if profile.photo and hasattr(profile.photo, 'url') is not None:
            photoUrl = info.context.build_absolute_uri(profile.photo.url)

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
            graduationYear=profile.graduationYear
        )

    @staticmethod
    def resolve_colleges(self, info, **kwargs):
        return College.objects.values().all()

    @staticmethod
    def resolve_isValidFace(self, info, **kwargs):
        photo = Profile.objects.get(user=info.context.user).photo
        imgUMat = cv2.imread(photo)
        image = cv2.cvtColor(imgUMat, cv2.COLOR_BGR2GRAY)
        detector = cv2.CascadeClassifier(FACE_DETECTOR_PATH)
        rects = detector.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5,
                                          minSize=(30, 30), flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
        rects = [(int(x), int(y), int(x + w), int(y + h)) for (x, y, w, h) in rects]
        return len(rects) == 1
