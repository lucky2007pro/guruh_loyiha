from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=17, blank=True, null=True)
    tg_username = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')

    def __str__(self):
        return self.username


class Saved(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='saved_by')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='saved_products')

    class Meta:
        unique_together = ('product', 'author')

    def __str__(self):
        return f"{self.author.username} saved {self.product.title}"


class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username}'s Wallet - {self.balance} sum"


class Card(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='cards')
    card_number = models.CharField(max_length=16)
    expiry_date = models.CharField(max_length=5)
    owner_name = models.CharField(max_length=150)

    def __str__(self):
        return f"Card {self.card_number[:4]}**** for {self.wallet.user.username}"
