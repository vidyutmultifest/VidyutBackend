from django.contrib import admin
from easy_select2 import select2_modelform

from .models import *


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    select2 = select2_modelform(Department, attrs={'width': '250px'})
    form = select2


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'dept', 'fee',)
    search_fields = ['name']
    select2 = select2_modelform(Competition, attrs={'width': '250px'})
    form = select2


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ('name', 'dept', 'fee',)
    select2 = select2_modelform(Workshop, attrs={'width': '250px'})
    form = select2


@admin.register(ContactPerson)
class ContactPersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email',)
