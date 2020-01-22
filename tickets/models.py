import uuid
from django.db import models
from django.contrib.auth.models import User

from payment.models import Order
from products.models import Product


class Ticket(models.Model):
    ticketID = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    purchaseTimestamp = models.DateTimeField()
    activationTimestamp = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ticketUser', null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='ticketOrder')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='ticketProduct')
    isCounterTicket = models.BooleanField(default=True)
    isActive = models.BooleanField(default=False)

    def __str__(self):
        return str(self.ticketID)


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