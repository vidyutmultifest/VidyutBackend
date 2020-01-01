import graphene
from django.contrib.auth.models import User
from graphql_jwt.decorators import login_required

from framework.api.helper import APIException
from participants.models import Team
from registrations.models import EventRegistration


class CreateTeamObj(graphene.ObjectType):
    hash = graphene.String()


class TeamUpdateStatusObj(graphene.ObjectType):
    status = graphene.Boolean()


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


class TeamEditDetailsObj(graphene.InputObjectType):
    name = graphene.String(required=False)
    leader = graphene.String(required=False)
    removeMembers = graphene.List(graphene.String, required=False)


class EditTeam(graphene.Mutation):
    class Arguments:
        teamHash = graphene.String(required=True)
        details = TeamEditDetailsObj(required=True)

    Output = TeamUpdateStatusObj

    @login_required
    def mutate(self, info, teamHash, details):
        user = info.context.user
        obj = Team.objects.get(hash=teamHash)

        # checks if team has already registered for some events
        rCount = EventRegistration.objects.filter(team=obj).count()
        if rCount > 0:
            raise APIException('You cannot edit a team after it has registered for an event.')

        # name change requested
        if details.name is not None:
            if obj.leader == user:
                obj.name = details.name
            else:
                raise APIException('You need to be the leader of the team to change its name')

        # leader change requested
        if details.leader is not None:
            if obj.leader == user:
                obj.leader = User.objects.get(username=details.leader)
            else:
                raise APIException('You need to be the current leader of the team to change its leader')

        # Removing members requested
        if details.removeMembers is not None:
            for member in details.removeMembers:
                delusr = User.objects.get(username=member)
                if obj.leader == user:
                    if delusr != user:
                        obj.members.remove(delusr)
                    else:
                        raise APIException('You cannot remove yourself from a team, in which you are the leader')
                else:
                    if delusr == user:
                        obj.members.remove(delusr)
                    else:
                        raise APIException(
                            'You cannot remove other members from your team, unless you are the leader'
                        )

            obj.save()  # saves changes
            return TeamUpdateStatusObj(status=True)


class DeleteTeam(graphene.Mutation):
    class Arguments:
        teamHash = graphene.String(required=True)

    Output = TeamUpdateStatusObj

    @login_required
    def mutate(self, info, teamHash):
        user = info.context.user
        obj = Team.objects.get(hash=teamHash)
        if obj.leader == user:

            # checks if team has already registered for some events
            rCount = EventRegistration.objects.filter(team=obj).count()
            if rCount > 0:
                raise APIException('You cannot delete a team after it has registered for an event.')

            obj.delete()
            return TeamUpdateStatusObj(status=True)
        else:
            raise APIException('You should be the leader of the team to delete the team')


class JoinTeam(graphene.Mutation):
    class Arguments:
        teamHash = graphene.String(required=True)

    Output = CreateTeamObj

    @login_required
    def mutate(self, info, teamHash):
        user = info.context.user
        try:
            obj = Team.objects.get(hash=teamHash)

            # checks if team has already registered for some events
            rCount = EventRegistration.objects.filter(team=obj).count()
            if rCount > 0:
                raise APIException('You cannot join a team after it has registered for an event.')

            obj.members.add(user)
            obj.save()
            return CreateTeamObj(hash=obj.hash)
        except Team.DoesNotExist:
            raise APIException('Team does not exist or have been deleted')


class Mutation(graphene.ObjectType):
    createTeam = CreateTeam.Field()
    deleteTeam = DeleteTeam.Field()
    editTeam = EditTeam.Field()
    joinTeam = JoinTeam.Field()
