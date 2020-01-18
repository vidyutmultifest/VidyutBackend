from datetime import datetime

import graphene
from graphql_jwt.decorators import login_required

from participants.models import Profile
from payment.models import Transaction
from registrations.models import EventRegistration


class MyNotificationObj(graphene.ObjectType):
    text = graphene.String()
    url = graphene.String()
    category = graphene.String()
    type = graphene.String()
    timestamp = graphene.String()


class Query(graphene.ObjectType):
    myNotifications = graphene.List(MyNotificationObj)

    @login_required
    def resolve_myNotifications(self, info):
        user = info.context.user
        n = []

        profile = Profile.objects.get(user=user)
        if profile.college is None:
            n.append({
                "text": "College details not entered. Please update your profile with college details",
                "url": "https://vidyut.amrita.edu/profile/edit-profile",
                "category": "profile",
                "type": "danger",
                "timestamp": datetime.now()
            })
        if profile.phone is None:
            n.append({
                "text": "Phone number not entered. Please update your profile with your phone number",
                "url": "https://vidyut.amrita.edu/profile/edit-profile",
                "category": "profile",
                "type": "danger",
                "timestamp": datetime.now()
            })

        registrations = EventRegistration.objects.filter(user=user)
        for reg in registrations:
            if reg.order and reg.order.transaction.isPaid or reg.event.price == '0':
                n.append({
                    "text": "You have successfully registered for " + reg.event.name,
                    "url": "https://vidyut.amrita.edu/my-registrations",
                    "category": "registration",
                    "type": "success",
                    "timestamp": reg.registrationTimestamp,
                })
            elif reg.order is None:
                n.append({
                    "text": "Pay for your registration of " + reg.event.name,
                    "url": "https://vidyut.amrita.edu/my-registrations",
                    "category": "registration",
                    "type": "warning",
                    "timestamp": reg.registrationTimestamp,
                })

        transactions = Transaction.objects.filter(user=user)
        for t in transactions:
            if t.isPaid:
                n.append({
                    "text": "Your transaction of Rs." + str(t.amount) + " is successful",
                    "url": "https://vidyut.amrita.edu/my-orders",
                    "category": "transaction",
                    "type": "success",
                    "timestamp": t.timestamp,
                })
            elif t.isProcessed is False:
                n.append({
                    "text":  "Your transaction #" + str(t.transactionID) + " of Rs." + str(t.amount) + " is under processing, please give us atleast a day for processing.",
                    "url": "https://vidyut.amrita.edu/help",
                    "category": "transaction",
                    "type": "warning",
                    "timestamp": t.timestamp,
                })
            elif t.isProcessed and t.isPaid is False:
                n.append({
                    "text": "Your transaction #" + str(t.transactionID) + " of Rs." + str(t.amount) + " has failed. If your money was debited, please contact help.",
                    "url": "https://vidyut.amrita.edu/help",
                    "category": "transaction",
                    "type": "danger",
                    "timestamp": t.timestamp,
                })
        return n
