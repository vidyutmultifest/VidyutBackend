import graphene

from events.models import Competition, Partners


class PartnerObj(graphene.ObjectType):
    name = graphene.String()
    about = graphene.String()
    logo = graphene.String()

    def resolve_name(self, info):
        return self.name

    def resolve_about(self, info):
        return self.about

    def resolve_logo(self, info):
        url = None
        if self.logo and hasattr(self.logo, 'url'):
            url = info.context.build_absolute_uri(self.logo.url)
        return url


class Query(object):
    listOrganizers = graphene.List(PartnerObj)

    def resolve_listOrganizers(self, info):
        list = []
        for org in Competition.objects.order_by().values_list('organiser', flat=True).distinct():
            if org is not None and org not in list:
                list.append(Partners.objects.get(id=org))
        return list
