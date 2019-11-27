from django.contrib import admin
from easy_select2 import select2_modelform

from .models import *


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price',)
    search_fields = ['name']
    select2 = select2_modelform(Product, attrs={'width': '250px'})
    form = select2


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    select2 = select2_modelform(PromoCode, attrs={'width': '250px'})
    form = select2
