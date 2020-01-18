import graphene

from participants.api.mutations.profile import Mutation as ProfileMutations
from participants.api.mutations.team import Mutation as TeamMutations
from participants.api.mutations.college import Mutation as CollegeMutations

from participants.api.query.profile import Query as ProfileQueries
from participants.api.query.rekognition import Query as RekognitionQueries
from participants.api.query.team import Query as TeamQueries
from participants.api.query.college import Query as CollegeQueries
from participants.api.query.myvidyut import Query as MyVidyutQueries
from participants.api.query.mynotifications import Query as MyNotificationQueries


class Mutation(
    ProfileMutations,
    TeamMutations,
    CollegeMutations,
    graphene.ObjectType
):
    pass


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
