from django.contrib import admin
from django.db.models.signals import post_save
from django.dispatch import receiver
from easy_select2 import select2_modelform
from products.models import *
from datetime import datetime

from .models import *


class CSInline(admin.TabularInline):
    model = CompetitionSchedule
    extra = 0
    select2 = select2_modelform(CompetitionSchedule, attrs={'width': '250px'})
    form = select2


class WSInline(admin.TabularInline):
    model = WorkshopSchedule
    extra = 0
    select2 = select2_modelform(WorkshopSchedule, attrs={'width': '250px'})
    form = select2


class TSInline(admin.TabularInline):
    model = TicketSchedule
    extra = 0
    select2 = select2_modelform(TicketSchedule, attrs={'width': '250px'})
    form = select2


@admin.register(Partners)
class PartnerAdmin(admin.ModelAdmin):
    select2 = select2_modelform(Partners, attrs={'width': '250px'})
    form = select2


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    select2 = select2_modelform(Department, attrs={'width': '250px'})
    form = select2


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Basic Details', {
            'fields': [
                ('name', 'slug'),
                'cover',
                ('dept', 'organiser', 'partners'),
                'hasSelectionProcess'
            ]
        }),
        ('Competition Details', {
            'fields': [
                'description',
                'details',
                'fee',
                ('firstPrize', 'secondPrize', 'thirdPrize')
            ]
        }),
        ('Contacts', {
            'fields': [
                'contacts'
            ]
        }),
        ('For Team Events', {
            'fields': [
                ('isTeamEvent', 'minTeamSize', 'maxTeamSize'),
            ]
        }),
        ('Form Fields (Do Not Touch)', {
            'fields': [
                'formFields'
            ]
        }),
        ('Curation (For Site Admins)', {
            'fields': [
                ('isRecommended', 'isPublished'),
            ]
        }),
    ]
    list_display = ('name', 'dept', 'fee', 'isPublished', 'lastEditor', 'lastEditTime')
    search_fields = ['name']
    select2 = select2_modelform(Competition, attrs={'width': '250px'})
    inlines = (CSInline,)
    form = select2

    def save_model(self, request, obj, form, change):
        obj.lastEditor = request.user
        obj.lastEditTime = datetime.now()
        super().save_model(request, obj, form, change)


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Basic Details', {
            'fields': [
                ('name', 'slug'),
                'cover',
                ('dept', 'organiser', 'partners'),
                'accreditedBy'
            ]
        }),
        ('Competition Details', {
            'fields': [
                'description',
                'details',
                'fee',
            ]
        }),
        ('Contacts', {
            'fields': [
                'contacts'
            ]
        }),
        ('Form Fields (Do Not Touch)', {
            'fields': [
                'formFields'
            ]
        }),
        ('Curation (For Site Admins)', {
            'fields': [
                ('isRecommended', 'isPublished'),
            ]
        }),
    ]
    list_display = ('name', 'dept', 'fee', 'isPublished', 'lastEditor', 'lastEditTime')
    select2 = select2_modelform(Workshop, attrs={'width': '250px'})
    form = select2
    inlines = (WSInline,)

    def save_model(self, request, obj, form, change):
        obj.lastEditor = request.user
        obj.lastEditTime = datetime.now()
        super().save_model(request, obj, form, change)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Basic Details', {
            'fields': [
                ('name', 'slug'),
                'cover',
                'organiser',
            ]
        }),
        ('Competition Details', {
            'fields': [
                'description',
                'details',
                'fee',
            ]
        }),
        ('Contacts', {
            'fields': [
                'contacts'
            ]
        }),
        ('Curation', {
            'fields': [
                ('isRecommended', 'isPublished'),
            ]
        }),
    ]
    list_display = ('name', 'isPublished', 'lastEditor', 'lastEditTime')
    select2 = select2_modelform(Ticket, attrs={'width': '250px'})
    form = select2
    inlines = (TSInline,)

    def save_model(self, request, obj, form, change):
        obj.lastEditor = request.user
        obj.lastEditTime = datetime.now()
        super().save_model(request, obj, form, change)


@admin.register(Merchandise)
class MerchandiseAdmin(admin.ModelAdmin):
    list_display = ('name', 'isPublished', 'lastEditor', 'lastEditTime')
    select2 = select2_modelform(Ticket, attrs={'width': '250px'})
    form = select2

    def save_model(self, request, obj, form, change):
        obj.lastEditor = request.user
        obj.lastEditTime = datetime.now()
        super().save_model(request, obj, form, change)


@admin.register(ContactPerson)
class ContactPersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email',)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    select2 = select2_modelform(TimeSlot, attrs={'width': '250px'})
    form = select2


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    select2 = select2_modelform(Venue, attrs={'width': '250px'})
    form = select2


# @receiver(post_save, sender=Competition)
# def create_Competition(sender, instance, created, **kwargs):
#     count = Product.objects.filter(competition=instance).count()
#     if count == 0:
#         Product.objects.create(competition=instance)
