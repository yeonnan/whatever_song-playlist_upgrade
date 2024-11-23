from django.db import models
from django.conf import settings
import uuid

class Chat(models.Model):
    room_nema = models.IntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)     # 메세지 보낸시간