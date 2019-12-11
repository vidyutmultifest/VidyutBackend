from django.contrib import admin
from easy_select2 import select2_modelform

from .models import *


@admin.register(EventRegistration)
class EventRegAdmin(admin.ModelAdmin):
    select2 = select2_modelform(EventRegistration, attrs={'width': '250px'})
    form = select2
