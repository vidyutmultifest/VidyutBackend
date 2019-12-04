import uuid
from django.db import models
from django.contrib.auth.models import User
from products.models import *


class Ticket(models.Model):
    ticketID = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    purchaseTimestamp = models.DateTimeField()
    activationTimestamp = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ticketUser', null=True, blank=True)
    purchaser = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ticketPurchaser')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='ticketProduct')
    isCounterTicket = models.BooleanField(default=True)
    isActive = models.BooleanField(default=False)

    def __str__(self):
        return str(self.ticketID)
