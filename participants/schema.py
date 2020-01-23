import graphene
import csv

from participants.api.mutations.profile import Mutation as ProfileMutations
from participants.api.mutations.team import Mutation as TeamMutations
from participants.api.mutations.college import Mutation as CollegeMutations

from participants.api.query.profile import Query as ProfileQueries
from participants.api.query.rekognition import Query as RekognitionQueries
from participants.api.query.team import Query as TeamQueries
from participants.api.query.college import Query as CollegeQueries
from participants.api.query.myvidyut import Query as MyVidyutQueries
from participants.api.query.mynotifications import Query as MyNotificationQueries
from participants.models import Profile, College


class Mutation(
    ProfileMutations,
    TeamMutations,
    CollegeMutations,
    graphene.ObjectType
):
    pass


# class SiteDataObj(graphene.ObjectType):
#     name = graphene.String()
#     vid = graphene.String()
#     email = graphene.String()
#     rollNo = graphene.String()
#     branch = graphene.String()
#     division = graphene.String()
#     year = graphene.String()
#
#
# class DataManager(graphene.ObjectType):
#     registered = graphene.List(SiteDataObj)
#     unregistered = graphene.List(SiteDataObj)
#
#     def resolve_registered(self, info):
#         return self['registered']


class Query(
    RekognitionQueries,
    ProfileQueries,
    TeamQueries,
    CollegeQueries,
    MyVidyutQueries,
    MyNotificationQueries,
    graphene.ObjectType
):
    pass
    # importUserData = graphene.Field(DataManager)
    #
    # def resolve_importUserData(self, info, **kwargs):
    #     registered = []
    #     unregistered = []
    #     with open('eng_data.csv', newline='') as csvfile:
    #         list = csv.reader(csvfile, delimiter=',')
    #         for user in list:
    #             name = user[0]
    #             rollNo = user[1]
    #             email = user[2]
    #             branch = user[3]
    #             division = user[4]
    #             year = user[5]
    #             try:
    #                 profile = Profile.objects.get(user__email=email)
    #                 vid = profile.vidyutID
    #                 profile.rollNo = rollNo
    #                 profile.college = College.objects.get(id=8)
    #                 profile.branch = branch
    #                 profile.admissionYear = year
    #                 profile.save()
    #                 obj = {
    #                     "name": name,
    #                     "rollNo": rollNo,
    #                     "email": email,
    #                     "vid": vid,
    #                     "year": year,
    #                     "branch": branch,
    #                     "division": division
    #                 }
    #                 print(obj)
    #                 registered.append(obj)
    #             except Profile.DoesNotExist:
    #                 obj = {
    #                     "name": name,
    #                     "rollNo": rollNo,
    #                     "email": email,
    #                     "year": year,
    #                     "branch": branch,
    #                     "division": division
    #                 }
    #                 unregistered.append(obj)
    #     return {
    #         "registered": registered,
    #         "unregistered": unregistered
    #     }
