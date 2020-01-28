from django.contrib import admin
from easy_select2 import select2_modelform

from .models import *


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Basic Details', {
            'fields': [
                'name',
                'isAvailable',
            ]
        }),
        ('Product', {
            'fields': [
                ('competition', 'workshop'),
                ('merchandise', 'ticket')
            ]
        }),
        ('Pricing', {
            'fields': [
                'price', 'isGSTAccounted'
            ]
        }),
        ('Restrictions', {
            'fields': [
                'isAmritapurianOnly', 'isFacultyOnly', 'isSchoolOnly', 'isOutsideOnly'
            ]
        }),
        ('Requirements', {
            'fields': [
                ('requireRegistration', 'requireEventRegistration'),
                ('requireAdvancePayment', 'restrictMultiplePurchases'),
            ]
        }),
        ('Registration', {
            'fields': [
                'showAgreementPage',
                'slots'
            ]
        }),
    ]
    list_display = ('name', 'price', 'slots', 'requireRegistration', 'isAmritapurianOnly', 'requireRegistration')
    list_filter = ('isAvailable', 'requireRegistration', 'isAmritapurianOnly', 'isFacultyOnly', 'isSchoolOnly', 'isOutsideOnly', 'isGSTAccounted')
    select2 = select2_modelform(Product, attrs={'width': '250px'})
    form = select2


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    select2 = select2_modelform(PromoCode, attrs={'width': '250px'})
    form = select2
