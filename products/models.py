from django.db import models
from users.models import CustomUser


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Product(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    address = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=17)
    tg_username = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True, null=True)
    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.title)

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.score for r in ratings) / ratings.count(), 1)
        return None

    def ratings_count(self):
        return self.ratings.count()

    class Meta:
        ordering = ('-id',)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images')


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='my_comments')
    body = models.TextField(verbose_name="Kommentariya matni")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kommentariya"
        verbose_name_plural = "Kommentariyalar"
        ordering = ['-date']

    def __str__(self):
        return f"{self.author.username} ning kommenti: {self.body[:20]}..."


class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('confirmed', 'Tasdiqlandi'),
        ('shipped', "Jo'natildi"),
        ('delivered', 'Yetkazib berildi'),
        ('cancelled', 'Bekor qilindi'),
    )
    PAYMENT_CHOICES = (
        ('wallet', 'Hamyon orqali'),
        ('cash', 'Naqd pul (Kuryer qo\'lida)'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    customer_name = models.CharField(max_length=150, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    is_paid = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    shipping_address = models.TextField()
    phone_number = models.CharField(max_length=17)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        product_title = self.product.title if self.product else 'Deleted Product'
        return f"{self.quantity} x {product_title} in Order #{self.order.id}"


class Rating(models.Model):
    SCORE_CHOICES = [(i, i) for i in range(1, 6)]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='my_ratings')
    score = models.PositiveSmallIntegerField(choices=SCORE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')
        verbose_name = "Reyting"
        verbose_name_plural = "Reytinglar"

    def __str__(self):
        return f"{self.user.username} -> {self.product.title}: {self.score}/5"
