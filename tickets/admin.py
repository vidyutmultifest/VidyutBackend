from django.contrib import admin
from easy_select2 import select2_modelform
from .models import *

from import_export import resources
from import_export.admin import ImportExportModelAdmin, ExportActionMixin


class PhysicalTicketResource(resources.ModelResource):
    class Meta:
        model = PhysicalTicket


@admin.register(PhysicalTicket)
class PhysicalTicketAdmin(ImportExportModelAdmin, ExportActionMixin, admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'number', 'issuer')
    search_fields = ('user__username', 'issuer__username', 'number')
    select2 = select2_modelform(PhysicalTicket, attrs={'width': '250px'})
    resource_class = PhysicalTicketResource
    form = select2


@admin.register(CheckInSession)
class CheckInSessionAdmin(admin.ModelAdmin):
    select2 = select2_modelform(CheckInSession, attrs={'width': '250px'})
    form = select2


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'session', 'issuer')
    select2 = select2_modelform(CheckIn, attrs={'width': '250px'})
    form = select2
