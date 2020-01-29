from django.db import models
from django.contrib.auth.models import User

from products.models import Product
from tickets.models import CheckInSession


class UserAccess(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    adminAccess = models.BooleanField(default=False)
    canAcceptPayment = models.BooleanField(default=False)
    viewAllTransactions = models.BooleanField(default=False)
    canIssueTickets = models.BooleanField(default=False)
    canViewProfiles = models.BooleanField(default=False)
    canViewRegistrations = models.BooleanField(default=False)
    productsManaged = models.ManyToManyField(Product, blank=True)
    canGeneralCheckIn = models.BooleanField(default=False)
    canCheckInUsers = models.BooleanField(default=False)
    sessionsManaged = models.ManyToManyField(CheckInSession, blank=True)

    def __str__(self):
        return self.user.username
