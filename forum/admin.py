from django.contrib import admin
from easy_select2 import select2_modelform

from .models import *


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    select2 = select2_modelform(Question, attrs={'width': '250px'})
    form = select2


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    select2 = select2_modelform(Answer, attrs={'width': '250px'})
    form = select2
