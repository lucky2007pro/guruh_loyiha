from django.urls import path
from .views import (
    new_product, product_detail, product_update,
    product_delete, new_comment, delete_comment, add_to_cart, cart_detail, checkout,
    product_list, rate_product, remove_from_cart, update_cart_item
)

app_name = 'products'

urlpatterns = [
    path('', product_list, name='index'),
    path('new/', new_product, name='new'),
    path('detail/<int:id>/', product_detail, name='detail'),
    path('update/<int:product_id>/', product_update, name='update'),
    path('delete/<int:product_id>/', product_delete, name='delete'),
    path('cart/add/', add_to_cart, name='add_to_cart'),
    path('cart/', cart_detail, name='cart_detail'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', update_cart_item, name='update_cart_item'),
    path('checkout/', checkout, name='checkout'),
    path('comment/<int:product_id>/', new_comment, name='new_comment'),
    path('comment-delete/<int:comment_id>/', delete_comment, name='delete_comment'),
    path('rate/<int:product_id>/', rate_product, name='rate_product'),
]