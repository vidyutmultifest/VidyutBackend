from django.contrib import admin
from .models import *
from easy_select2 import select2_modelform


class op_inline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    select2 = select2_modelform(OrderProduct, attrs={'width': '250px'})
    form = select2


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transactionID', 'isSuccessful', 'amount', 'user', 'timestamp',)
    select2 = select2_modelform(Transaction, attrs={'width': '250px'})
    form = select2


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('orderID', 'user', 'timestamp',)
    inlines = (op_inline,)
    select2 = select2_modelform(Order, attrs={'width': '250px'})
    form = select2

