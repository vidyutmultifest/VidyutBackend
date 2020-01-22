from django.contrib import admin
from easy_select2 import select2_modelform

from .models import *


from import_export import resources
from import_export.admin import ImportExportModelAdmin, ExportActionMixin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin


class UserResource(resources.ModelResource):
    class Meta:
        model = User


class UserAdmin(ImportExportModelAdmin, ExportActionMixin, DefaultUserAdmin):
    resource_class = UserResource
    pass


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    select2 = select2_modelform(Team, attrs={'width': '250px'})
    list_display = ('name', 'leader', 'allowEditing',)
    form = select2


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'vidyutID', 'admissionYear', 'college')
    list_filter = ('college', 'admissionYear')
    search_fields = ['vidyutID', 'user__username', 'phone', 'admissionYear']
    select2 = select2_modelform(Profile, attrs={'width': '250px'})
    form = select2


@admin.register(College)
class LanguageAdmin(admin.ModelAdmin):
    select2 = select2_modelform(College, attrs={'width': '250px'})
    form = select2