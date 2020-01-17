from django.contrib import admin
from easy_select2 import select2_modelform

from .models import *


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    select2 = select2_modelform(Team, attrs={'width': '250px'})
    form = select2


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    select2 = select2_modelform(Member, attrs={'width': '250px'})
    form = select2
