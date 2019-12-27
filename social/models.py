import uuid
from django.db import models


class Feed(models.Model):
    name = models.CharField(max_length=50)


class Story(models.Model):
    def get_image_path(self, filename):
        ext = filename.split('.')[-1]
        filename = 'vidyut_stories_' + "%s.%s" % (uuid.uuid4(), ext)
        return 'static/social/stories/' + filename

    created = models.DateTimeField(auto_now_add=True, blank=True)
    image = models.ImageField(upload_to=get_image_path)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
