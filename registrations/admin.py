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


@admin.register(EventRegistration)
class EventRegAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'team', 'registrationTimestamp', 'transactionStatus')
    list_filter = (('registrationTimestamp', DateTimeRangeFilter), 'event', TransactionStatusFilter)
    select2 = select2_modelform(EventRegistration, attrs={'width': '250px'})
    form = select2

    def transactionStatus(self, obj):
        if obj.order:
            if obj.order.transaction:
                if obj.order.transaction.isPaid:
                    return "Paid"
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

