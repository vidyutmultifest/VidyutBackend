import uuid

from django.contrib.auth.models import User
from django.db import models

from participants.models import Team
from payment.models import Order
from products.models import Product


class EventRegistration(models.Model):
    regID = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='registeredUser', null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='registeredTeam', null=True, blank=True)
    event = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='registeredEvent', null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='registeredEvent', null=True, blank=True)
    formData = models.TextField(null=True, blank=True)
    emailSend = models.BooleanField(default=False)
    registrationTimestamp = models.DateTimeField()
    isSelected = models.BooleanField(default=True)

    def __str__(self):
        return str(self.regID)
