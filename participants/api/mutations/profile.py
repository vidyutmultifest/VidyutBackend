import graphene
from graphql_jwt.decorators import login_required

from framework.api.helper import APIException
from participants.models import Profile, College
from tickets.models import PhysicalTicket


class UpdateProfileObj(graphene.ObjectType):
    status = graphene.Boolean()


class ProfileDetailsObj(graphene.InputObjectType):
    firstName = graphene.String(required=False)
    lastName = graphene.String(required=False)
    rollNo = graphene.String(required=False)
    phone = graphene.String(required=False)
    location = graphene.String(required=False)
    gender = graphene.String(required=False)
    emergencyPhone = graphene.String(required=False)
    emergencyContactName = graphene.String(required=False)
    foodPreference = graphene.String(required=False)
    shirtSize = graphene.String(required=False)
    degreeType = graphene.String(required=False)
    graduationYear = graphene.String(required=False)
    collegeID = graphene.Int(required=False)
    isFaculty = graphene.Boolean(required=False)
    isSchoolStudent = graphene.Boolean(required=False)


class UpdateProfile(graphene.Mutation):
    class Arguments:
        details = ProfileDetailsObj(required=False)

    Output = UpdateProfileObj

    @login_required
    def mutate(self, info, details=None):
        user = info.context.user
        profile = Profile.objects.get(user=user)
        physicalTicket = PhysicalTicket.objects.filter(user=info.context.user)
        if info.context.FILES is not None and physicalTicket.count() == 0:
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
                user.save()
            if details.lastName is not None:
                user.last_name = details.lastName
                user.save()
            if details.rollNo is not None:
                profile.rollNo = details.rollNo
            if details.phone is not None:
                profile.phone = details.phone
            if details.location is not None:
                profile.location = details.location
            if details.gender is not None:
                profile.gender = details.gender
            if details.emergencyPhone is not None:
                profile.emergencyPhone = details.emergencyPhone
            if details.emergencyContactName is not None:
                profile.emergencyContactName = details.emergencyContactName
            if details.foodPreference is not None:
                profile.foodPreference = details.foodPreference
            if details.shirtSize is not None and physicalTicket.count() == 0:
                profile.shirtSize = details.shirtSize
            if details.degreeType is not None:
                profile.degreeType = details.degreeType
            if details.graduationYear is not None:
                profile.admissionYear = int(details.graduationYear)
            if details.isFaculty is not None:
                profile.isFaculty = details.isFaculty
            if details.isSchoolStudent is not None:
                profile.isSchoolStudent = details.isSchoolStudent
            if details.collegeID is not None:
                try:
                    college = College.objects.get(id=details.collegeID)
                    profile.college = college
                except College.DoesNotExist:
                    raise APIException('College does not exist or has been removed.')
        profile.save()

        return UpdateProfileObj(status=True)


class Mutation(graphene.ObjectType):
    updateProfile = UpdateProfile.Field()
