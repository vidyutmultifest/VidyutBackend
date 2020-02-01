from django.contrib import admin
from django.db.models import Q

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


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('amount', 'issuer')
    select2 = select2_modelform(Refund, attrs={'width': '250px'})
    form = select2


@admin.register(Transaction)
class TransactionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('transactionID', 'amount', 'user', 'isProcessed', 'isPending', 'isPaid', 'isOnline', 'issuer', 'timestamp', 'issuerLocation')
    list_select_related = (
        'user',
        'issuer'
    )
    list_filter = (
        ('timestamp', DateTimeRangeFilter),
        'isPaid',
        'isPending',
        'isProcessed',
        'isOnline',
        'amount',
        'issuer'
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


class PaymentModeFilter(admin.SimpleListFilter):
    title = 'Payment Mode'
    parameter_name = 'Payment Mode'

    def lookups(self, request, model_admin):
        return (
            ('Online', 'Online'),
            ('Offline', 'Offline'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Online':
            return queryset.filter(transaction__isOnline=True)
        elif value == 'Offline':
            return queryset.filter(transaction__isOnline=False)
        return queryset


class EmailTypeFilter(admin.SimpleListFilter):
    title = 'Email Type'
    parameter_name = 'Email Type'

    def lookups(self, request, model_admin):
        return (
            ('gmail', 'GMail'),
            ('amrita-in', 'Amrita am.stu / ay ID'),
            ('amrita-out', 'Amrita other ID'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'gmail':
            return queryset.filter(user__email__contains='@gmail.com')
        elif value == 'amrita-in':
            return queryset.filter(Q(user__email__contains='am.students.amrita.edu') | Q(user__email__contains='ay.amrita.edu'))
        elif value == 'amrita-out':
            return queryset.exclude(Q(user__email__contains='am.students.amrita.edu') | Q(user__email__contains='ay.amrita.edu')).filter(user__email__contains='amrita.edu')
        return queryset


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('orderID', 'user', 'timestamp', 'transactionStatus')
    list_filter = (
        ('timestamp', DateTimeRangeFilter),
        'products',
        TransactionStatusFilter,
        PaymentModeFilter,
        EmailTypeFilter
    )
    filter_horizontal = ('products',)
    search_fields = ['orderID', 'user__username', 'transaction__transactionID', 'products__name']
    autocomplete_fields = ['transaction']
    date_hierarchy = 'timestamp'
    inlines = (OPInline,)
    select2 = select2_modelform(Order, attrs={'width': '250px'})
    form = select2

    def transactionStatus(self, obj):
        if obj.transaction:
            if obj.transaction.isPaid:
                if obj.transaction.isOnline:
                    return "Paid Online"
                else:
                    if obj.transaction.issuer:
                        return "Collected by " + obj.transaction.issuer.username
                    else:
                        return "Paid Offline"
            elif obj.transaction.isPending:
                return "Pending"
            elif obj.transaction.isProcessed:
                return "Rejected"
            else:
                return "Not Processed"
        else:
            return "No Trans"

    transactionStatus.short_description = 'Transaction Status'
