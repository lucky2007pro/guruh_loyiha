from django.urls import path
from .views import (
    new_product, product_detail, product_update,
    product_delete, new_comment, delete_comment
)

app_name = 'products'

urlpatterns = [
    path('new/', new_product, name='new'),
    path('detail/<int:id>/', product_detail, name='detail'),
    path('update/<int:product_id>/', product_update, name='update'),
    path('delete/<int:product_id>/', product_delete, name='delete'),
    path('comment/<int:product_id>/', new_comment, name='new_comment'),
    path('comment-delete/<int:comment_id>/', delete_comment, name='delete_comment'),
]