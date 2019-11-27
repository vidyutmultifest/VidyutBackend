from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField()
    description = models.CharField(max_length=200)
    price = models.IntegerField()

    def __str__(self):
        return self.name


class PromoCode(models.Model):
    code = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    products = models.ManyToManyField(Product, blank=True)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.code
