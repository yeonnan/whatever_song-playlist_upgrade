from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    nickname = models.CharField(max_length=50)
    image = models.ImageField(upload_to='accounts/profile_pics/%Y/%m/%d/', blank=True, null=True, default='accounts/profile_pics/logo.png/')