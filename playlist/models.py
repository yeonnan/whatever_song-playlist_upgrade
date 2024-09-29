from django.db import models
from django.conf import settings
    

class Playlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    playlist_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)  
    link = models.URLField()
    image_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
