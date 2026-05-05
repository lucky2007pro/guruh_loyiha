from django.shortcuts import render
from django.views import View
from products.models import Product, Category
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
# Create your views here.

def for_all_pages(requests):
    categories = Category.objects.all()
    cart_count = 0
    if requests.user.is_authenticated:
        cart = getattr(requests.user, 'cart', None)
        if cart:
            cart_count = cart.items.count()
    return {"categories": categories, "cart_count": cart_count}

class IndexView(View):
    def get(self, request):
        products = Product.objects.select_related('category').prefetch_related('productimage_set')
        q = request.GET.get('q', '')
        category_id = request.GET.get('category', '')
        if q:
            products = products.filter(title__icontains=q)
        if category_id and category_id != 'all':
            products = products.filter(category_id=category_id)
        paginator = Paginator(products, 12)
        page_obj = paginator.get_page(request.GET.get('page'))
        return render(request, 'index.html', {
            'products': page_obj,
            'page_obj': page_obj,
            'is_paginated': paginator.num_pages > 1,
            'selected_category': category_id,
        })

class CategoryView(View):
    def get(self, request, category_name):
        category = get_object_or_404(Category, name=category_name)
        products = Product.objects.filter(category=category)
        q = request.GET.get('q', '')
        if q:
            products = products.filter(title__icontains=q)
        return render(request, 'category.html', {'products': products, 'category': category})

PAGES = {
    'about': {'title': 'Kompaniya haqida', 'content': 'JobEasy Mall - sifatli va ishonchli xaridlar platformasi! Biz 2026 yilda tashkil topganmiz va hozirgi kunda yozgi eng top kiyimlarni siz aziz hammayurtlarga hamyonbop narxlarda taklif etamiz. O\'zbekiston bo\'ylab savdo xizmatini yo\'lga qo\'yish bilan birga...'},
    'mission': {'title': 'Bizning missiya', 'content': 'Bizning asosiy missiyamiz har bir xaridorga sifatli va qulay mahsulotlarni eng yaqin narxlarda uyigacha eltib berish va doimiy a\'lo kayfiyat ulashishdir. Raqamli raqobat bozori ichida eng yuqori foydalanuvchi tajribasini (User Experience) taqdim etishga intilamiz.'},
    'careers': {'title': 'Ochiq vakansiyalar', 'content': 'Bizning jamoaga qo\'shiling! Hozirda quvvatli Dasturchilar (Backend & Frontend v.k) va Kuryerlarni izlayapmiz. Telegram orqali +998901234567 raqamiga murojaat qilishingiz mumkin.'},
    'partners': {'title': 'Hamkorlarimiz', 'content': 'Bizning hamkorlar - respublikaning yetakchi ishlab chiqaruvchilari va taniqli brendlar. Kafolatlangan va ishonchli logistika agentliklari bilan yaqindan ish olib boramiz ishonch uchun rahmat!'},
    'delivery': {'title': 'Yetkazib berish (Delivery)', 'content': 'Toshkent shahri bo\'ylab yetkazib berish 1-2 kunni oladi. Viloyatlarga eshikgacha yoki viloyat markazlarigacha maxsus pochta tizimimiz asosida 3-4 kunda boradi.'},
    'payment-methods': {'title': 'To\'lov usullari', 'content': 'Onlayn hamda Oflyne ko\'rinishda (Kuryer maxsulotni topshirgandan so\'ng Payme, Click, naqd) amalga oshirish mumkin.'},
    'returns': {'title': 'Qaytarish va almashish', 'content': 'Agar xarid qilingan mahsulot yaroqsiz bo\'lsa (zavod braki) yoxud sifatsiz holatda yetkazilsa 7 ish kuni ichida qaytarib berishingiz yoki boshqasiga bepul almashtirishingiz kafolatlanadi.'},
    'support': {'title': 'Mijozlarni qo\'llab-quvvatlash', 'content': 'Bizning call-markaz mutaxassislari kun-u tun xizmatingizda! Istalgan savolingiz bilan +998 (71) 000-00-00 raqamiga aloqaga chiqishingiz mumkin.'},
    'terms': {'title': 'Foydalanish qoidalari', 'content': 'Ilovadagi har bir hisob fiktiv xarid va spamlarga qarshi nazorat ostida saqlanadi. Biz barcha foydalanuvchilar qoidalarga doimiy amal qilishlarini so\'rab qolamiz.'},
    'privacy': {'title': 'Maxfiylik siyosati', 'content': 'Sayt foydalanuvchilarining ishonchini qadrlaydi va har bir maxfiy ma\'lumotni himoya qiladi va uchinchi shaxslarga umuman sizdirilmaydi.'},
    'oferta': {'title': 'Ommaviy oferta', 'content': 'Hurmatli xaridor, ushbu oferta sotuvchi va xaridor munosabatlarning barcha qoidalarini bitim tarzida ifoda etadi...'},
    'faq': {'title': 'FAQ qanday hisoblanadi?', 'content': 'Bu bo\'limda kelajakda xaridorlardan kelgan barcha qiziq va umumiy savollar hamda ularning yechimlari nashr etiladi!'},
}

from django.shortcuts import redirect

class StaticPageView(View):
    def get(self, request, slug):
        page = PAGES.get(slug)
        if not page:
            return redirect('main:index')
        return render(request, 'static_page.html', {'page': page})
