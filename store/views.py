from django.shortcuts import render,get_object_or_404
from .models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage,Paginator,PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q

def store(request,category_slug = None):
    categories =None
    Products = None
    if category_slug != None:
        categories = get_object_or_404(Category,slug = category_slug)
        products = Product.objects.filter(category = categories,is_available = True)
        paginator = Paginator(products,2)# this will display only 2 things of 1st argument(product) in 1 page
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available = True).order_by('id')
        paginator = Paginator(products,3)# this will display only 6 things of 1st argument(product) in 1 page
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        product_count = products.count()
    context = {
    'products': paged_product, # we are passing paged product(6 products only)
    'product_count':product_count
    }
    return render(request,'store/store.html',context)
# Create your views here.

def search(request):
    if 'keyword' in request.GET:
        keyword  = request.GET['keyword']
        #return HttpResponse(keyword)
        #exit()
        if keyword:
            products = Product.objects.order_by('created_date').filter(Q(description__icontains=keyword) | Q(Product_name__icontains=keyword)) # Q is django function to handle complex queries
            product_count = products.count()
    context = {
    'products': products,
    'product_count':product_count,
    }
    return render(request,'store/store.html',context)


def product_detail(request,category_slug,product_slug):

    try:
        single_product = Product.objects.get(category__slug=category_slug,slug = product_slug) #category__slug -- double underscore -- used to go to category and get slug value from category module
        in_cart  = CartItem.objects.filter(cart__cart_id = _cart_id(request),product = single_product).exists()
    except Exception as e:
        raise e
    context = {
    'single_product': single_product,
    'in_cart':in_cart,

    }
    return render(request,'store/product_details.html',context)
