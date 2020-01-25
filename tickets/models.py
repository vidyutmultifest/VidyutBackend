import uuid
from django.db import models
from django.contrib.auth.models import User

from payment.models import Order
from products.models import Product


class CheckInSession(models.Model):
    sessionID = models.UUIDField(unique=True, default=uuid.uuid1, editable=False)
    isActive = models.BooleanField(default=False)
    allowMultipleCheckIn = models.BooleanField(default=False)
    allowCheckOut = models.BooleanField(default=False)
    products = models.ManyToManyField(Product)

    def __str__(self):
        return str(self.sessionID)


class CheckIn(models.Model):
    session = models.ForeignKey(CheckInSession, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkInUser')
    issuer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='checkInIssuer')
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user.username)


class PhysicalTicket(models.Model):
    number = models.CharField(max_length=15, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='PhysicalTicketUser')
    issuer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='PhysicalTicketIssuer')
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user.username)
