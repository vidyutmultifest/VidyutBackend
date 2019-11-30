import uuid

from django.db import models
from products.models import *
from django.contrib.auth.models import User


class Transaction(models.Model):
    transactionID = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField()
    amount = models.PositiveIntegerField()
    manualIssue = models.BooleanField(default=False)
    isSuccessful = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='transactionUser')
    issuer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='transactionIssuer', null=True, blank=True)
    issuerLocation = models.CharField(max_length=50, null=True, blank=True)
    issuerDevice = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.transactionID)


class Order(models.Model):
    orderID = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    transaction = models.ForeignKey(Transaction, on_delete=models.PROTECT)
    promoCode = models.ForeignKey(PromoCode, on_delete=models.PROTECT, null=True, blank=True)
    products = models.ManyToManyField(Product, through='OrderProduct')

    def __str__(self):
        return str(self.orderID)


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Order Products"
        verbose_name = "Order Product"
