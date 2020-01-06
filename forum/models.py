from django.contrib.auth.models import User
from django.db import models

from products.models import Product


class Question(models.Model):
    question = models.TextField()
    askedBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.question)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.answer)
