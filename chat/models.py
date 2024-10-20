from django.db import models
from django.conf import settings
import uuid

class Chat(models.Model):
    message_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)      # 메세지 고유 식별자
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)     # 메세지 보낸시간