from django.contrib import admin
from .models import *
from easy_select2 import select2_modelform
from rangefilter.filter import DateTimeRangeFilter
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class TransactionResource(resources.ModelResource):

    class Meta:
        model = Transaction
        fields = ('transactionID', 'isPaid', 'isProcessed', 'isPending', 'amount', 'user__username', 'user__first_name', 'issuer__username', 'timestamp', 'issuerLocation', 'issuerDevice', )


class OPInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    select2 = select2_modelform(OrderProduct, attrs={'width': '250px'})
    form = select2


@admin.register(Transaction)
class TransactionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('transactionID', 'isProcessed', 'isPending', 'isPaid', 'amount', 'user', 'issuer', 'timestamp', 'issuerLocation')
    list_select_related = (
        'user',
        'issuer'
    )
    list_filter = (
        ('timestamp', DateTimeRangeFilter),
        'isPaid',
        'isPending',
        'isProcessed',
        'amount',
    )
    date_hierarchy = 'timestamp'
    search_fields = ['transactionID', 'user__username', 'issuer__username', 'isPaid', 'amount']
    select2 = select2_modelform(Transaction, attrs={'width': '250px'})
    form = select2
    resource_class = TransactionResource


class TransactionStatusFilter(admin.SimpleListFilter):
    title = 'Transaction Status'
    parameter_name = 'TransactionStatus'

    def lookups(self, request, model_admin):
        return (
            ('Paid', 'Paid'),
            ('Pending', 'Pending'),
            ('Rejected', 'Rejected'),
            ('NotProcessed', 'NotProcessed'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Paid':
            return queryset.filter(transaction__isPaid=True)
        elif value == 'Pending':
            return queryset.filter(transaction__isPending=True)
        elif value == 'Rejected':
            return queryset.filter(
                transaction__isPaid=False,
                transaction__isPending=False,
                transaction__isProcessed=True
            )
        elif value == 'NotProcessed':
            return queryset.filter(transaction__isProcessed=False)
        return queryset


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('orderID', 'user', 'timestamp', 'transactionStatus')
    list_filter = (('timestamp', DateTimeRangeFilter), 'products', TransactionStatusFilter)
    filter_horizontal = ('products',)
    search_fields = ['orderID', 'user__username', 'transaction__transactionID', 'products__name']
    autocomplete_fields = ['transaction']
    date_hierarchy = 'timestamp'
    inlines = (OPInline,)
    select2 = select2_modelform(Order, attrs={'width': '250px'})
    form = select2

    def transactionStatus(self, obj):
        if obj.transaction.isPaid:
            return "Paid"
        elif obj.transaction.isPending:
            return "Pending"
        elif obj.transaction.isProcessed:
            return "Rejected"
        else:
            return "Not Processed"

    transactionStatus.short_description = 'Transaction Status'
