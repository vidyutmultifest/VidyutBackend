import graphene
from graphql_jwt.decorators import login_required

from participants.models import College


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


class Mutation(graphene.ObjectType):
    addCollege = AddCollege.Field()
