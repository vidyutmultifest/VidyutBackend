from django.contrib import admin
from easy_select2 import select2_modelform
from rangefilter.filter import DateTimeRangeFilter

from .models import *


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
            return queryset.filter(order__transaction__isPaid=True)
        elif value == 'Pending':
            return queryset.filter(order__transaction__isPending=True)
        elif value == 'Rejected':
            return queryset.filter(
                order__transaction__isPaid=False,
                order__transaction__isPending=False,
                order__transaction__isProcessed=True
            )
        elif value == 'NotProcessed':
            return queryset.filter(order__transaction__isProcessed=False)
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
            return queryset.filter(order__transaction__isOnline=True)
        elif value == 'Offline':
            return queryset.filter(order__transaction__isOnline=False)
        return queryset


@admin.register(EventRegistration)
class EventRegAdmin(admin.ModelAdmin):
    search_fields = ('regID', 'user__username', 'team__name', 'event__name')
    list_display = ('event', 'owner', 'registrationTimestamp', 'transactionStatus', 'transactionAmt', 'emailSend')
    list_filter = (('registrationTimestamp', DateTimeRangeFilter), TransactionStatusFilter, PaymentModeFilter)
    select2 = select2_modelform(EventRegistration, attrs={'width': '250px'})
    form = select2

    def owner(self, obj):
        if obj.user:
            return obj.user.username
        else:
            return obj.team.name

    def transactionAmt(self, obj):
        if obj.order:
            if obj.order.transaction:
                return str(obj.order.transaction.amount)
        return "N/A"

    def transactionStatus(self, obj):
        if obj.order:
            if obj.order.transaction:
                if obj.order.transaction.isPaid:
                    if obj.order.transaction.isOnline:
                        return "Paid Online"
                    else:
                        return "Paid Offline"
                elif obj.order.transaction.isPending:
                    return "Pending"
                elif obj.order.transaction.isProcessed:
                    return "Rejected"
                else:
                    return "Not Processed"
            else:
                return "No Trans"
        else:
            return "No Order"

    transactionStatus.short_description = 'Transaction Status'

