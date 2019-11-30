import uuid

from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver


class College(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    def get_selfie_path(self, filename):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        return 'static/uploads/profile/selfies/' + filename

    def get_id_path(self, filename):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        return 'static/uploads/profile/collegeID/' + filename

    vidyutID = models.CharField(max_length=256, unique=True)
    vidyutHash = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='Profile',
        verbose_name='User',
    )
    college = models.ForeignKey(College, on_delete=models.PROTECT, null=True, blank=True)
    photo = models.ImageField(upload_to=get_selfie_path, null=True, blank=True)
    idPhoto = models.ImageField(upload_to=get_id_path, null=True, blank=True)
    graduationYear = models.IntegerField(null=True, blank=True)
    rollNo = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    location = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_item(sender, instance, **kwargs):
    p, created = Profile.objects.get_or_create(user=instance)
    if created:
        p.vidyutID = 'V' + str(1000 + p.user.id)
        p.save()
