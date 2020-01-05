import graphene
from .models import Story, Feed


class StoryObj(graphene.ObjectType):
    created = graphene.String()
    image = graphene.String()
    id = graphene.String()
    link = graphene.String()

    def resolve_image(self, info):
        url = None
        if self['image'] is not '':
            url = info.context.build_absolute_uri(self['image'])
        return url


class FeedObj(graphene.ObjectType):
    name = graphene.String()
    stories = graphene.List(StoryObj)

    def resolve_stories(self, info):
        return Story.objects.values().filter(feed=self['id']).order_by('-created')


class Query(object):
    viewStories = graphene.List(FeedObj)

    @staticmethod
    def resolve_viewStories(self, info):
        feeds = Story.objects.all().values_list('feed', flat=True)
        return Feed.objects.values().filter(id__in=feeds)
