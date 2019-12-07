from django.contrib import admin
from easy_select2 import select2_modelform

from .models import *


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    select2 = select2_modelform(Team, attrs={'width': '250px'})
    form = select2


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'vidyutID', 'graduationYear', 'college')
    list_filter = ('college', 'graduationYear')
    search_fields = ['vidyutID', 'user__username', 'phone', 'graduationYear']
    select2 = select2_modelform(Profile, attrs={'width': '250px'})
    form = select2


@admin.register(College)
class LanguageAdmin(admin.ModelAdmin):
    select2 = select2_modelform(College, attrs={'width': '250px'})
    form = select2