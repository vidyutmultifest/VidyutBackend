import csv
import json
from io import StringIO
from django.core.mail import EmailMessage

from django.core.management.base import BaseCommand


from framework import settings
from participants.models import Profile
from payment.models import Transaction, Order

from_email = settings.EMAIL_HOST_USER


class Command(BaseCommand):
    help = 'Exports & Sends online payment list to an email as a CSV'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str)

    def handle(self, *args, **options):
        senderEmail = options['email']
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
                print([
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
            except Order.DoesNotExist:
                pass

        csvfile = StringIO()
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(list)

        email = EmailMessage(
            "Online Payment List for ACRD",
            'Please find the attachment.',
            from_email,
            ['web@vidyut.amrita.edu', senderEmail],
        )
        email.attach('online-payment-list.csv', csvfile.getvalue(), 'text/csv')
        email.send()

