from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView as BaseGraphQLView
from django.conf.urls import url, include


class GraphQLView(BaseGraphQLView):

    @staticmethod
    def format_error(error):
        formatted_error = super(GraphQLView, GraphQLView).format_error(error)
        del formatted_error['locations']
        del formatted_error['path']
        try:
            formatted_error['context'] = error.original_error.context
        except AttributeError:
            pass

        return formatted_error


urlpatterns = [
    path('admin/', admin.site.urls),
    url('', include('social_django.urls', namespace='social')),
    path('', csrf_exempt(GraphQLView.as_view(graphiql=True))),
]

urlpatterns = [
    url('api/', include(urlpatterns))
]

admin.site.index_title = 'Vidyut Admin Dashboard'
admin.site.site_title = 'Vidyut Backend'