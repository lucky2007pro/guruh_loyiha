from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, ProductImage, Comment
from .forms import ProductForm, NewProductForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages


# Create your views here.

@login_required(login_url='login')
def new_product(request):
    if request.method == 'GET':
        form = NewProductForm()
        return render(request, 'products/new_product.html', {'form': form})

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

        return render(request, 'products/new_product.html', {'form': form})


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    if "recently_viewed" in request.session:
        r_viewed = request.session["recently_viewed"]
        if product.id not in r_viewed:
            r_viewed.append(product.id)
            request.session.modified = True
    else:
        request.session["recently_viewed"] = [product.id]

    return render(request, 'products/product_detail.html', {'product': product})


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