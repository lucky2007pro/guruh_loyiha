import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ProductForm, NewProductForm
from .models import Product, Category, ProductImage, Comment, Cart, CartItem, Order, OrderItem, Rating


# Create your views here.

@login_required(login_url='login')
def new_product(request):
    if request.method == 'GET':
        form = NewProductForm()
        return render(request, 'new_product.html', {'form': form})

    elif request.method == 'POST':
        form = NewProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.author = request.user
            product.save()

            productimages = []
            for image in request.FILES.getlist('images'):
                productimages.append(ProductImage(image=image, product=product))

            if productimages:
                ProductImage.objects.bulk_create(productimages)

            messages.success(request, 'Mahsulot muvaffaqiyatli yaratildi!')
            return redirect('main:index')

        return render(request, 'new_product.html', {'form': form})


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    if "recently_viewed" in request.session:
        r_viewed = request.session["recently_viewed"]
        if product.id not in r_viewed:
            r_viewed.append(product.id)
            request.session.modified = True
            Product.objects.filter(id=product.id).update(view_count=product.view_count + 1)
    else:
        request.session["recently_viewed"] = [product.id]
        Product.objects.filter(id=product.id).update(view_count=product.view_count + 1)

    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(product=product, user=request.user).first()

    comments = product.comments.select_related('author').all()
    images = product.productimage_set.all()

    return render(request, 'products_detail.html', {
        'product': product,
        'user_rating': user_rating,
        'comments': comments,
        'images': images,
    })


@login_required(login_url='login')
def product_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user == product.author:
        if request.method == 'GET':
            form = ProductForm(instance=product)
            return render(request, 'product_update.html', {'form': form, 'pr': product})

        elif request.method == 'POST':
            form = ProductForm(instance=product, data=request.POST, files=request.FILES)
            if form.is_valid():
                form.save()

                if request.FILES.getlist('images'):
                    ProductImage.objects.filter(product=product).delete()
                    productimages = []
                    for image in request.FILES.getlist("images"):
                        productimages.append(ProductImage(image=image, product=product))
                    ProductImage.objects.bulk_create(productimages)

                messages.success(request, 'Successfully Updated!')
                return redirect('products:detail', id=product.id)

            return render(request, 'product_update.html', {'form': form, 'pr': product})
    else:
        messages.error(request, 'Access denied!')
        return redirect('main:index')


@login_required(login_url='login')
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user == product.author:
        if request.method == 'POST':
            product.delete()
            messages.info(request, 'O\'chirildi')
            return redirect('main:index')

        return render(request, 'product_delete.html', {'pr': product})
    else:
        messages.error(request, 'Amal bajarilmagan!')
        return redirect('main:index')


@login_required(login_url='login')
def new_comment(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        Comment.objects.create(product=product, author=request.user, body=request.POST['body'])
        messages.success(request, 'Comment added!')
        return redirect('products:detail', id=product_id)

    return HttpResponse('Method not allowed', status=405)


@login_required(login_url='login')
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    product_id = comment.product.id

    if request.user == comment.author:
        comment.delete()
        messages.success(request, 'Comment deleted!')
        return redirect('products:detail', id=product_id)

    return redirect('products:detail', id=product_id)


@login_required(login_url='login')
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = data.get('quantity', 1)
            product = get_object_or_404(Product, id=product_id)
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not item_created:
                cart_item.quantity += quantity
                cart_item.save()
            else:
                cart_item.quantity = quantity
                cart_item.save()
            return JsonResponse({'success': True, 'msg': "Savatchaga qo'shildi"})
        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)}, status=400)
    return JsonResponse({'success': False}, status=405)


@login_required(login_url='login')
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total_price = sum(item.product.price * item.quantity for item in items if item.product)
    return render(request, 'cart.html', {'cart': cart, 'items': items, 'total_price': total_price})


@login_required(login_url='login')
def checkout(request):
    from users.models import Wallet
    from decimal import Decimal

    cart = getattr(request.user, 'cart', None)
    if not cart or not cart.items.exists():
        messages.error(request, "Savatingiz bo'sh")
        return redirect('main:index')

    items = cart.items.select_related('product').all()
    total_price = sum(item.product.price * item.quantity for item in items if item.product)
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        address = request.POST.get('shipping_address', '').strip()
        phone = request.POST.get('phone_number', '').strip()
        customer_name = request.POST.get('customer_name', '').strip()
        payment_method = request.POST.get('payment_method', 'cash')

        if not address or not phone or not customer_name:
            messages.error(request, "Barcha maydonlarni to'ldiring.")
            return render(request, 'checkout.html', {
                'items': items, 'total_price': total_price, 'wallet': wallet
            })

        # Wallet to'lov
        if payment_method == 'wallet':
            wallet.refresh_from_db()
            if wallet.balance < total_price:
                messages.error(
                    request,
                    f"Hamyonda yetarli mablag' yo'q. Balans: {wallet.balance} so'm, "
                    f"kerak: {total_price} so'm."
                )
                return render(request, 'checkout.html', {
                    'items': items, 'total_price': total_price, 'wallet': wallet
                })
            # Hisobdan yeching
            wallet.balance = wallet.balance - Decimal(str(total_price))
            wallet.save()
            is_paid = True
        else:
            is_paid = False

        order = Order.objects.create(
            user=request.user,
            customer_name=customer_name,
            total_price=total_price,
            shipping_address=address,
            phone_number=phone,
            payment_method=payment_method,
            is_paid=is_paid,
        )

        for item in items:
            if item.product:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity,
                )

        cart.items.all().delete()

        if payment_method == 'wallet':
            messages.success(
                request,
                f"Buyurtmangiz qabul qilindi! Hamyondan {total_price} so'm yechildi. "
                f"Qolgan balans: {wallet.balance} so'm."
            )
        else:
            messages.success(request, "Buyurtmangiz qabul qilindi! Kuryer kelganda to'laysiz.")

        return redirect('users:orders')

    return render(request, 'checkout.html', {
        'items': items,
        'total_price': total_price,
        'wallet': wallet,
    })


def product_list(request):
    products = Product.objects.select_related('category', 'author').prefetch_related('productimage_set', 'ratings')
    categories = Category.objects.all()

    q = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort = request.GET.get('sort', 'latest')

    if q:
        products = products.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if category_id:
        products = products.filter(category_id=category_id)
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'popular':
        products = products.order_by('-view_count')
    else:
        products = products.order_by('-id')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'product_list.html', {
        'products': page_obj,
        'categories': categories,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
    })


@login_required(login_url='login')
def rate_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        try:
            score = int(request.POST.get('score', 0))
            if 1 <= score <= 5:
                Rating.objects.update_or_create(
                    product=product, user=request.user,
                    defaults={'score': score}
                )
                messages.success(request, f'Reytingingiz ({score}/5) saqlandi!')
            else:
                messages.error(request, 'Noto\'g\'ri reyting qiymati.')
        except (ValueError, TypeError):
            messages.error(request, 'Xato yuz berdi.')
    return redirect('products:detail', id=product_id)


@login_required(login_url='login')
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        cart = getattr(request.user, 'cart', None)
        if cart:
            CartItem.objects.filter(id=item_id, cart=cart).delete()
            messages.success(request, 'Savatdan o\'chirildi.')
    return redirect('products:cart_detail')


@login_required(login_url='login')
def update_cart_item(request, item_id):
    if request.method == 'POST':
        cart = getattr(request.user, 'cart', None)
        if cart:
            try:
                qty = int(request.POST.get('quantity', 1))
                if qty > 0:
                    CartItem.objects.filter(id=item_id, cart=cart).update(quantity=qty)
                else:
                    CartItem.objects.filter(id=item_id, cart=cart).delete()
            except (ValueError, TypeError):
                pass
    return redirect('products:cart_detail')
