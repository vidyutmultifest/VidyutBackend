import graphene
from graphql_jwt.decorators import login_required

from registrations.models import EventRegistration
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


class CreateTeamObj(graphene.ObjectType):
    hash = graphene.String()


class CreateTeam(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    Output = CreateTeamObj

    @login_required
    def mutate(self, info, name):
        leader = info.context.user
        obj = Team.objects.create(name=name, leader=leader)
        obj.members.add(leader)
        obj.save()
        return CreateTeamObj(hash=obj.hash)


class ProfileDetailsObj(graphene.InputObjectType):
    name = graphene.String(required=False)
    removeMembers = graphene.List(graphene.String)


# class EditTeam(graphene.Mutation):
#     class Arguments:
#         teamHash = graphene.String(required=True)
#         details = ProfileDetailsObj(required=True)
#
#     Output = graphene.Boolean()
#
#     @login_required
#     def mutate(self, info, teamHash, details):
#         user = info.context.user
#         obj = Team.objects.get(hash=teamHash)
#         if obj.leader == user:
#             if details.name is not None:
#                 obj.name = details.name
#             if details.removeMembers is not None:
#                 for member in details.removeMembers:
#                     delusr = User.objects.get(username=member)
#                     if delusr != user:
#                         obj.members.reverse(delusr)
#             obj.save()
#             return True
#         return False


class DeleteTeam(graphene.Mutation):
    class Arguments:
        teamHash = graphene.String(required=True)

    Output = graphene.Boolean()

    @login_required
    def mutate(self, info, teamHash):
        user = info.context.user
        obj = Team.objects.get(hash=teamHash)
        if obj.leader == user:
            rCount = EventRegistration.objects.filter(team=obj).count()
            if rCount > 0:
                return False
            obj.delete()
            return True
        return False


class JoinTeam(graphene.Mutation):
    class Arguments:
        teamHash = graphene.String(required=True)

    Output = CreateTeamObj

    @login_required
    def mutate(self, info, teamHash):
        user = info.context.user
        obj = Team.objects.get(hash=teamHash)
        obj.members.add(user)
        obj.save()
        return CreateTeamObj(hash=obj.hash)


class Mutation(updateProfileMutation, graphene.ObjectType):
    addCollege = AddCollege.Field()
    createTeam = CreateTeam.Field()
    deleteTeam = DeleteTeam.Field()
    # editTeam = EditTeam.Field()
    joinTeam = JoinTeam.Field()


class CollegeObj(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    location = graphene.String()

    # DEPRECIATED
    @staticmethod
    def resolve_location(self, info):
        return None


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
    gender = graphene.String()
    emergencyPhone = graphene.String()
    emergencyContactName = graphene.String()
    foodPreference = graphene.String()
    shirtSize = graphene.String()
    degreeType = graphene.String()


class TeamMemberObj(graphene.ObjectType):
    name = graphene.String()
    username = graphene.String()


class TeamObj(graphene.ObjectType):
    name = graphene.String()
    leader = graphene.Field(TeamMemberObj)
    members = graphene.List(TeamMemberObj)
    isUserLeader = graphene.Boolean()


class Query(rekognitionQueries, object):
    isProfileComplete = graphene.Boolean()
    myProfile = graphene.Field(ProfileObj)
    colleges = graphene.List(CollegeObj)
    getTeam = graphene.Field(TeamObj, hash=graphene.String(required=True))
    myTeams = graphene.List(TeamObj)
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

        idPhotoUrl = None
        if profile.idPhoto and hasattr(profile.idPhoto, 'url') is not None:
            idPhotoUrl = info.context.build_absolute_uri(profile.idPhoto.url)

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
            idPhoto=idPhotoUrl,
            graduationYear=profile.graduationYear,
            rollNo=profile.rollNo,
            degreeType=profile.degreeType,
            gender=profile.gender,
            emergencyPhone=profile.emergencyPhone,
            emergencyContactName=profile.emergencyContactName,
            foodPreference=profile.foodPreference,
            shirtSize=profile.shirtSize,
            location=profile.location
        )

    @staticmethod
    def resolve_colleges(self, info, **kwargs):
        return College.objects.values().all()

    @login_required
    def resolve_getTeam(self, info, **kwargs):
        user = info.context.user
        team = Team.objects.get(hash=kwargs.get('hash'))
        if user in team.members.all():
            mlist = []
            for member in team.members.all():
                mlist.append({
                    "name": member.first_name + ' ' + member.last_name,
                    "username": member.username
                })
            return TeamObj(
                name=team.name,
                leader={
                    "name": team.leader.first_name + ' ' + team.leader.last_name,
                    "username": team.leader.username
                },
                members=mlist,
                isUserLeader=user == team.leader
            )
        return None


    @login_required
    def resolve_myTeams(self, info, **kwargs):
        user = info.context.user
        teams = Team.objects.filter(members=user)
        tlist = []
        for team in teams:
            mlist = []
            for member in team.members.all():
                mlist.append({
                    "name": member.first_name + ' ' + member.last_name,
                    "username": member.username
                })
            tlist.append({
                "name": team.name,
                "leader": {
                    "name": team.leader.first_name + ' ' + team.leader.last_name,
                    "username": team.leader.username
                },
                "members": mlist,
                "isUserLeader": False
            })
        return tlist

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
