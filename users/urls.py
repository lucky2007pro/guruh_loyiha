from .views import (
    SignUpView, ProfileView, UpdateProfileView, AddRemoveSavedView, SavedView,
    RecentlyViewedView, WalletView, AddCardView, DepositView, WithdrawView,
    DeleteCardView, OrderHistoryView, ClearRecentlyViewedView
)
from django.urls import path

app_name='users'
urlpatterns = [
    path('signup', SignUpView.as_view(), name='signup'),
    path('profile/<str:username>', ProfileView.as_view(), name='profile'),
    path('update', UpdateProfileView.as_view(), name='update'),
    path('addremovesaved/<int:product_id>', AddRemoveSavedView.as_view(), name='addremovesaved'),
    path('saveds', SavedView.as_view(), name='saveds'),
    path('recently-viewed', RecentlyViewedView.as_view(), name='recently_viewed'),
    path('clear-viewed/', ClearRecentlyViewedView.as_view(), name='clear_viewed'),
    path('wallet/', WalletView.as_view(), name='wallet'),
    path('wallet/add-card/', AddCardView.as_view(), name='add_card'),
    path('wallet/deposit/', DepositView.as_view(), name='deposit'),
    path('wallet/withdraw/', WithdrawView.as_view(), name='withdraw'),
    path('wallet/delete-card/<int:card_id>/', DeleteCardView.as_view(), name='delete_card'),
    path('orders/', OrderHistoryView.as_view(), name='orders'),
]