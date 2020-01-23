import csv
import json
from django.core.management.base import BaseCommand


from framework import settings
from participants.models import Profile
from payment.models import Transaction, Order

from_email = settings.EMAIL_HOST_USER


class Command(BaseCommand):
    help = 'Exports & Sends Registration form applications to an email as a CSV'


    def handle(self, *args, **options):
        transactions = Transaction.objects.filter(isPaid=True, isOnline=True)
        list = []
        for t in transactions:
            profile = Profile.objects.get(user=t.user)
            try:
                order = Order.objects.get(transaction=t)
                college = 'N/A'
                if profile.college:
                    college = profile.college.name
                name = t.user.first_name + ' ' + t.user.last_name
                transactionID = 'VIDYUT' + str(t.transactionID)
                email = t.user.email
                phone = profile.phone
                amount = t.amount
                timestamp = t.timestamp
                productName = 'N/A'
                if order.products.count() > 0:
                    productName = order.products.first().name
                bankrefno = 'N/A'
                if t.transactionData and json.loads(t.transactionData):
                    a = json.loads(t.transactionData)
                    bankrefno = a["bankrefno"]
                list.append([
                    transactionID,
                    bankrefno,
                    name,
                    email,
                    phone,
                    college,
                    amount,
                    timestamp,
                    productName
                ])
                print('a')
            except Order.DoesNotExist:
                pass
        with open('acrd-list.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(list)
