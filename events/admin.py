from django.contrib import admin
from django.db.models.signals import post_save
from django.dispatch import receiver
from easy_select2 import select2_modelform
from products.models import *

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


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    select2 = select2_modelform(Ticket, attrs={'width': '250px'})
    form = select2


@admin.register(Merchandise)
class MerchandiseAdmin(admin.ModelAdmin):
    select2 = select2_modelform(Ticket, attrs={'width': '250px'})
    form = select2


@admin.register(ContactPerson)
class ContactPersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email',)


@receiver(post_save, sender=Competition)
def create_Competition(sender, instance, created, **kwargs):
    count = Product.objects.filter(competition=instance).count()
    if count == 0:
        Product.objects.create(competition=instance)


@receiver(post_save, sender=Workshop)
def create_Workshop(sender, instance, created, **kwargs):
    count = Product.objects.filter(workshop=instance).count()
    if count == 0:
        Product.objects.create(workshop=instance)


@receiver(post_save, sender=Ticket)
def create_Ticket(sender, instance, created, **kwargs):
    count = Product.objects.filter(ticket=instance).count()
    if count == 0:
        Product.objects.create(ticket=instance)


@receiver(post_save, sender=Merchandise)
def create_Merchandise(sender, instance, created, **kwargs):
    count = Product.objects.filter(merchandise=instance).count()
    if count == 0:
        Product.objects.create(merchandise=instance)
