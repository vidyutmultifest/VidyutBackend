import uuid

from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Member(models.Model):
    def get_photo_path(self, filename):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        return 'static/uploads/crew/photos/' + filename

    name = models.CharField(max_length=150)
    photo = models.ImageField(upload_to=get_photo_path, null=True, blank=True)
    role = models.CharField(max_length=200)
    isHead = models.BooleanField(default=False)
    isCore = models.BooleanField(default=False)
    isFaculty = models.BooleanField(default=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

