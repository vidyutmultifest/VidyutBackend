from django.contrib import admin
from .models import Feed, Story
from easy_select2 import select2_modelform


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    select2 = select2_modelform(Feed, attrs={'width': '250px'})
    form = select2


@admin.register(Story)
class FeedAdmin(admin.ModelAdmin):
    select2 = select2_modelform(Story, attrs={'width': '250px'})
    form = select2
