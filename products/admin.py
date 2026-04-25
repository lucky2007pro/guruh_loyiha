from django.contrib import admin
from .models import Category, Product, ProductImage, Comment, Cart, CartItem, Order, OrderItem
# Register your models here.

class ProductImageInline(admin.TabularInline):
    model = ProductImage

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'date','author', 'category')
    inlines = [ProductImageInline]

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Comment)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)