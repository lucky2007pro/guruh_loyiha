from django.shortcuts import render, redirect
from django.views.generic import UpdateView

from .forms import SignUpForm, UpdateProfileForm
from django.views import View
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import CustomUser, Saved
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from products.models import Product
# Create your views here.

class SignUpView(UserPassesTestMixin, View):
    def get(self, request):
        return render(request, 'registration/signup.html')

    def post(self, request):
        form = SignUpForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Muvaffaqiyatli ro\'yhatdan o\'tdingiz!')
            return redirect('login')
        return render(request, 'registration/signup.html', {'form': form})

    def test_func(self):
        user = self.request.user
        if user.is_authenticated:
            return False
        return True

class ProfileView(View):
    def get(self, request, username):
        user = get_object_or_404(CustomUser, username=username)
        return render(request, 'profile.html', {'user': user})

class UpdateProfileView(LoginRequiredMixin, View):
    login_url = '/login/'
    def get(self, request):
        form = UpdateProfileForm(instance=request.user)
        return render(request, 'profile_update.html', {'form': form})

    def post(self, request):
        form = UpdateProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil muvaffaqiyatli yangilandi!')
            return redirect('profile', request.user.username)
        return render(request, 'profile_update.html', {'form': form})

class AddRemoveSavedView(LoginRequiredMixin, View):
    login_url = '/login/'
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        saved_product = Saved.objects.filter(product=product, author=request.user).first()
        if saved_product:
            saved_product.delete()
            messages.success(request, 'Removed from saved!')
        else:
            Saved.objects.create(product=product, author=request.user)
            messages.success(request, 'Added to saved!')
        return redirect(request.META.get('HTTP_REFERER'))


class SavedView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        saveds = Saved.objects.filter(author=request.user)
        q = request.GET.get('q', '')
        if q:
            products = Product.objects.filter(title__icontains=q)
            saveds = Saved.objects.filter(author=request.user, product__in=products)
        return render(request, 'saved_products.html', {"saveds": saveds})


class RecentlyViewedView(View):
    def get(self, request):
        if not "recently_viewed" in request.session:
            products = []
        else:
            r_viewed = request.session["recently_viewed"]
            products = Product.objects.filter(id__in=r_viewed)
            q = request.GET.get('q', '')
            if q:
                products = products.filter(title__icontains=q)
        return render(request, "viewed_products.html", {'products': products})


from django.db.models import F
from .models import Wallet, Card
from decimal import Decimal

class WalletView(LoginRequiredMixin, View):
    login_url = '/login/'
    def get(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        cards = wallet.cards.all()
        return render(request, 'wallet.html', {'wallet': wallet, 'cards': cards})

class AddCardView(LoginRequiredMixin, View):
    login_url = '/login/'
    def post(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        card_number = request.POST.get('card_number')
        expiry_date = request.POST.get('expiry_date')
        owner_name = request.POST.get('owner_name')
        if card_number and expiry_date and owner_name:
            Card.objects.create(wallet=wallet, card_number=card_number, expiry_date=expiry_date, owner_name=owner_name)
            messages.success(request, 'Karta muvaffaqiyatli qo\'shildi')
        else:
            messages.error(request, 'Barcha maydonlarni to\'ldiring')
        return redirect('users:wallet')

class DepositView(LoginRequiredMixin, View):
    login_url = '/login/'
    def post(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        amount = request.POST.get('amount')
        card_id = request.POST.get('card_id')
        if amount and card_id:
            try:
                amt = Decimal(amount)
                if amt > 0:
                    wallet.balance = F('balance') + amt
                    wallet.save()
                    wallet.refresh_from_db()
                    messages.success(request, f"Hamyoningizga {amt} so'm tushirildi.")
                else:
                    messages.error(request, "Ijobiy qiymat kiriting.")
            except:
                messages.error(request, "Xato summa kiritildi.")
        return redirect('users:wallet')

class WithdrawView(LoginRequiredMixin, View):
    login_url = '/login/'
    def post(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        amount = request.POST.get('amount')
        card_id = request.POST.get('card_id')
        if amount and card_id:
            try:
                amt = Decimal(amount)
                if amt > 0 and wallet.balance >= amt:
                    wallet.balance = F('balance') - amt
                    wallet.save()
                    wallet.refresh_from_db()
                    messages.success(request, f"Hamyoningizdan {amt} so'm yecholib, kartaga o'tkazildi.")
                elif wallet.balance < amt:
                    messages.error(request, "Hamyonda yetarli mablag' yo'q.")
                else:
                    messages.error(request, "Ijobiy qiymat kiriting.")
            except:
                messages.error(request, "Xato summa kiritildi.")
        return redirect('users:wallet')