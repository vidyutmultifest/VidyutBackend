import graphene
import graphql_jwt
import graphql_social_auth

from participants.schema import Query as ParticipantQueries


class Query(ParticipantQueries, graphene.ObjectType):
    pass


class UserType(graphene.ObjectType):
    username = graphene.Field(graphene.String)


class SocialAuth(graphql_social_auth.SocialAuthJWT):
    user = graphene.Field(UserType)
    token = graphene.String()

    @classmethod
    def resolve(cls, root, info, social, **kwargs):
        try:
            from graphql_jwt.shortcuts import get_token, get_refresh_token, create_refresh_token
        except ImportError:
            raise ImportError(
                'django-graphql-jwt not installed.\n'
                'Use `pip install \'django-graphql-social-auth[jwt]\'`.')
        return cls(user=social.user, token=get_token(social.user))


class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    social_auth = SocialAuth.Field()


schema = graphene.Schema(mutation=Mutation, query=Query)
