import csv
from io import StringIO

from django.contrib.auth.models import User
from django.core.mail import EmailMessage

from django.core.management.base import BaseCommand
from django.db.models import Q

from framework import settings
from participants.models import Profile
from payment.models import Order
from registrations.models import EventRegistration

from_email = settings.EMAIL_HOST_USER


class Command(BaseCommand):
    help = 'Exports & sends list of participants to an email as a CSV'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str)
        parser.add_argument('coordinates', type=str)


    def handle(self, *args, **options):
        senderEmail = options['email']
        coordinates = options['coordinates']
        list = []

        users = Order.objects.filter(
            Q(transaction__isPaid=True) &
            Q(
                Q(transaction__issuerLocation__startswith=coordinates)
                | Q(transaction__user__email__startswith='BL.EN')
            )
        ).values_list('user__id', flat=True).distinct()
        for u in users:
            list.append(u)

        teamregs = EventRegistration.objects.filter(
            Q(order__transaction__isPaid=True) & Q(user=None) &
            Q(
                Q(order__transaction__issuerLocation__startswith=coordinates)
                | Q(order__transaction__user__email__startswith='BL.EN')
            )
        )
        for t in teamregs:
            for u in t.team.members.all():
                if u.id not in list:
                    list.append(u.id)

        data = [['Name', 'College', 'Gender', 'Phone', 'Email']]
        for u in list:
            user = User.objects.get(id=u)
            profile = Profile.objects.get(user=user)
            name = user.first_name + ' ' + user.last_name
            college = 'N/A'
            if profile.college:
                college = profile.college.name
            gender = profile.gender
            phone = profile.phone
            email = user.email
            print([name, college, gender, phone, email])
            data.append([name, college, gender, phone, email])

        csvfile = StringIO()
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data)

        email = EmailMessage(
            "Participant list for Vidyut 2020",
            'Please find the attachment.',
            from_email,
            ['web@vidyut.amrita.edu', senderEmail],
        )
        email.attach('outside-participant-list.csv', csvfile.getvalue(), 'text/csv')
        email.send()

