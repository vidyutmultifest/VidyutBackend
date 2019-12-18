import uuid
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from events.models import Workshop, Competition, Merchandise, Ticket


class Product(models.Model):
    productID = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    workshop = models.ForeignKey(Workshop, on_delete=models.PROTECT, null=True, blank=True)
    competition = models.ForeignKey(Competition, on_delete=models.PROTECT, null=True, blank=True)
    merchandise = models.ForeignKey(Merchandise, on_delete=models.PROTECT, null=True, blank=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.PROTECT, null=True, blank=True)

    price = models.PositiveIntegerField(null=True, blank=True)
    isAvailable = models.BooleanField(default=True)
    slots = models.PositiveIntegerField(null=True, blank=True)

    requireRegistration = models.BooleanField(default=False)
    requireAdvancePayment = models.BooleanField(default=False)
    restrictMultiplePurchases = models.BooleanField(default=True)

    isAmritapurianOnly = models.BooleanField(default=False)
    isFacultyOnly = models.BooleanField(default=False)
    isSchoolOnly = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def product(self):
        if self.workshop is not None:
            return self.workshop
        if self.competition is not None:
            return self.competition
        if self.ticket is not None:
            return self.ticket
        if self.merchandise is not None:
            return self.merchandise
        return None


class PromoCode(models.Model):
    code = models.CharField(max_length=100, unique=True)
    isActive = models.BooleanField(default=False)
    description = models.CharField(max_length=200)
    products = models.ManyToManyField(Product, blank=True)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.code
