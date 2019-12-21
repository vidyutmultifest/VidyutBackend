import uuid
from django.db import models

from products.models import *
from django.contrib.auth.models import User

from framework import settings

from_email = settings.EMAIL_HOST_USER


class Transaction(models.Model):
    transactionID = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField()
    amount = models.PositiveIntegerField()
    manualIssue = models.BooleanField(default=False)
    isOnline = models.BooleanField(default=False)
    isProcessed = models.BooleanField(default=False)
    isPending = models.BooleanField(default=False)
    isPaid = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='transactionUser')
    issuer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='transactionIssuer', null=True, blank=True)
    issuerLocation = models.CharField(max_length=50, null=True, blank=True)
    issuerDevice = models.CharField(max_length=100, null=True, blank=True)
    transactionData = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.transactionID)


class Order(models.Model):
    orderID = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    transaction = models.OneToOneField(Transaction, on_delete=models.PROTECT, null=True, blank=True)
    promoCode = models.ForeignKey(PromoCode, on_delete=models.PROTECT, null=True, blank=True)
    products = models.ManyToManyField(Product, through='OrderProduct')

    def __str__(self):
        return str(self.orderID)


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Order Products"
        verbose_name = "Order Product"


# @receiver(post_save, sender=Transaction)
# def onPayTrans(sender, instance, **kwargs):
#     if instance.isPaid:
#         order = Order.objects.get(transaction=instance)
#         htmly = get_template('./emails/payment-confirmation.html')
#         d = {
#             'name': instance.user.first_name,
#             'transactionID': str(instance.transactionID),
#             'orderID': str(order.orderID),
#             'amount': str(instance.amount),
#             'paymentMode': 'offline',
#             'issuer': instance.issuer.first_name
#         }
#         html_content = htmly.render(d)
#         send_mail(
#             'Payment Confirmation for Order #' + str(order.orderID),
#             strip_tags(html_content),
#             from_email,
#             [instance.user.email],
#             html_message=html_content,
#             fail_silently=False,
#         )
