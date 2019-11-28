from django.db import models
from django.contrib.auth.models import User


class UserAccess(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    adminAccess = models.BooleanField(default=False)
    canAcceptPayment = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
