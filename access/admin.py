from django.contrib import admin
from easy_select2 import select2_modelform
from .models import *


@admin.register(UserAccess)
class UserAccessAdmin(admin.ModelAdmin):
    select2 = select2_modelform(UserAccess, attrs={'width': '250px'})
    form = select2