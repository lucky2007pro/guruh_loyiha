from django.contrib import admin
from .models import Category, Product, ProductImage, Comment, Cart, CartItem, Order, OrderItem, Rating
# Register your models here.

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('author', 'date')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'date', 'author', 'category', 'price', 'view_count')
    list_filter = ('category', 'date')
    search_fields = ('title', 'description', 'author__username')
    inlines = [ProductImageInline, CommentInline]

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    search_fields = ('name',)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'product', 'date', 'body')
    list_filter = ('date',)
    search_fields = ('author__username', 'body')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'payment_method', 'is_paid', 'total_price', 'created_at')
    list_filter = ('status', 'payment_method', 'is_paid', 'created_at')
    search_fields = ('user__username', 'customer_name', 'phone_number')
    list_editable = ('status', 'is_paid')
    inlines = [OrderItemInline]

class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'score', 'created_at')
    list_filter = ('score',)
    search_fields = ('user__username', 'product__title')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Rating, RatingAdmin)