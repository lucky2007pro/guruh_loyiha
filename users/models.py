from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=17, blank=True, null=True)
    tg_username = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')

    def __str__(self):
        return self.username


class Comment(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='my_comments'
    )
    body = models.TextField(verbose_name="Kommentariya matni")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kommentariya"
        verbose_name_plural = "Kommentariyalar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username} ning kommenti: {self.body[:20]}..."