import graphene

from crew.models import Member


class CrewTeamObj(graphene.ObjectType):
    name = graphene.String()
    color = graphene.String()


class MemberObj(graphene.ObjectType):
    name = graphene.String()
    photo = graphene.String()
    role = graphene.String()
    team = graphene.Field(CrewTeamObj)
    isHead = graphene.Boolean()
    isCore = graphene.Boolean()
    isFaculty = graphene.Boolean()

    def resolve_photo(self, info):
        if self.photo and hasattr(self.photo, 'url'):
            return info.context.build_absolute_uri(self.photo.url)
        return None


class Query(graphene.ObjectType):
    listCrew = graphene.List(MemberObj)

    def resolve_listCrew(self, info, **kwargs):
        return Member.objects.all().distinct().order_by('-isCore', 'isFaculty', '-isHead', 'team__name', 'name')
