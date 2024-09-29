from django.db import models
from django.conf import settings


class Post(models.Model):
    class category(models.TextChoices):
        RECOMMEND = "노래 추천", "노래 추천"
        FREE = "자유", "자유"

    title = models.CharField(max_length=50)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    author_nickname = models.CharField(max_length=50)
    link = models.URLField(blank=True, null=True)
    image = models.ImageField(
        upload_to="posts/post_pic/%Y/%m/%d/", blank=True, null=True, default="posts/post_pic/main logo.png/"
    )
    category = models.CharField(
        max_length=5, blank=True, choices=category.choices
    )
    like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="post_likes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_nickname = models.CharField(max_length=50)
    content = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
