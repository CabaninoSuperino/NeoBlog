from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(
        upload_to='posts/images/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    like_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class SubPost(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="subposts")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} (подпост для {self.post.title})"




