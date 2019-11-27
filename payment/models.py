import uuid

from django.db import models
from products.models import *
from django.contrib.auth.models import User


class Transaction(models.Model):
    transactionID = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField()
    amount = models.PositiveIntegerField()
    manualIssue = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='transactionUser')
    issuer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='transactionIssuer')

    def __str__(self):
        return str(self.transactionID)


class Order(models.Model):
    orderID = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField()
    products = models.ManyToManyField(Product)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    transaction = models.ForeignKey(Transaction, on_delete=models.PROTECT)
    promoCode = models.ForeignKey(PromoCode, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return str(self.orderID)
