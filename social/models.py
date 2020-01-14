import uuid
from django.db import models


class Feed(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Story(models.Model):
    def get_image_path(self, filename):
        ext = filename.split('.')[-1]
        filename = 'vidyut_stories_' + "%s.%s" % (uuid.uuid4(), ext)
        return 'static/social/stories/' + filename

    name = models.CharField(max_length=50, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    image = models.ImageField(upload_to=get_image_path)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    link = models.URLField(null=True, blank=True)

    def __str__(self):
        return str(self.id)


class Slide(models.Model):
    def get_image_path(self, filename):
        ext = filename.split('.')[-1]
        filename = 'vidyut_slide_' + "%s.%s" % (uuid.uuid4(), ext)
        return 'static/social/slides/' + filename

    name = models.CharField(max_length=50, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    image = models.ImageField(upload_to=get_image_path)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    link = models.URLField(null=True, blank=True)