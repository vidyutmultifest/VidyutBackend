import graphene


class CollegeObj(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    location = graphene.String()

    # DEPRECIATED
    @staticmethod
    def resolve_location(self, info):
        return None


class TeamMemberObj(graphene.ObjectType):
    name = graphene.String()
    username = graphene.String()


class TeamObj(graphene.ObjectType):
    name = graphene.String()
    leader = graphene.Field(TeamMemberObj)
    members = graphene.List(TeamMemberObj)
    membersCount = graphene.Int()
    isUserLeader = graphene.Boolean()
    hash = graphene.String()
    isEditable = graphene.Boolean()
    document = graphene.String()


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
    isFaculty = graphene.Boolean()
    isSchoolStudent = graphene.Boolean()
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
    hasEventsRegistered = graphene.Boolean()
