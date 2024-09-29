from django.db import models
from django.conf import settings


class Playlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    playlist_id = models.CharField(max_length=255) 

