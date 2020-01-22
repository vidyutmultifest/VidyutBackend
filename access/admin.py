from django.contrib import admin
from easy_select2 import select2_modelform
from .models import *


@admin.register(UserAccess)
class UserAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'canViewRegistrations', 'adminAccess', 'canAcceptPayment')
    list_filter = ('canViewRegistrations', 'canAcceptPayment')
    select2 = select2_modelform(UserAccess, attrs={'width': '250px'})
    form = select2
