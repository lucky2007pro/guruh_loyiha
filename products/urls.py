from django.urls import path
from django.views.generic import RedirectView
from .views import (
    new_product, product_detail, product_update,
    product_delete, new_comment, delete_comment, add_to_cart, cart_detail, checkout
)

app_name = 'products'

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='main:index'), name='index'),
    path('new/', new_product, name='new'),
    path('detail/<int:id>/', product_detail, name='detail'),
    path('update/<int:product_id>/', product_update, name='update'),
    path('delete/<int:product_id>/', product_delete, name='delete'),
    path('cart/add/', add_to_cart, name='add_to_cart'),
    path('cart/', cart_detail, name='cart_detail'),
    path('checkout/', checkout, name='checkout'),
    path('comment/<int:product_id>/', new_comment, name='new_comment'),
    path('comment-delete/<int:comment_id>/', delete_comment, name='delete_comment'),
]