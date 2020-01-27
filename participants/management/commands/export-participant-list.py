import csv
from io import StringIO

from django.contrib.auth.models import User
from django.core.mail import EmailMessage

from django.core.management.base import BaseCommand
from django.db.models import Q

from framework import settings
from participants.models import Profile
from registrations.models import EventRegistration

from_email = settings.EMAIL_HOST_USER


class Command(BaseCommand):
    help = 'Exports & sends list of participants to an email as a CSV'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str)

    def handle(self, *args, **options):
        senderEmail = options['email']
        list = []

        indregs = EventRegistration.objects.filter(
            order__transaction__isPaid=True, team=None
        ).exclude(
            Q(user__email__contains='am.students.amrita.edu') |
            Q(user__email__contains='ay.amrita.edu')
        ).values_list('user__id', flat=True).distinct()
        for u in indregs:
            list.append(u)

        teamregs = EventRegistration.objects.filter(
            order__transaction__isPaid=True, user=None
        ).exclude(
              Q(team__leader__email__contains='am.students.amrita.edu') |
              Q(team__leader__email__contains='ay.amrita.edu')
        )
        for t in teamregs:
            for u in t.team.members.all():
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

