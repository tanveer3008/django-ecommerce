from django.shortcuts import render,get_object_or_404,redirect
from .models import Product,ReviewRating
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage,Paginator,PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct

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
    if request.user.is_authenticated:
        try:
            orderproduct=OrderProduct.objects.filter(user=request.user,product_id=single_product.id).exists()
        except orderproduct.ObjectDoesNotExist:
            orderproduct=None
    else:
        orderproduct=None
    #Reviews
    reviews=ReviewRating.objects.filter(product_id=single_product.id , status=True)
    context = {
    'single_product': single_product,
    'in_cart':in_cart,
    'orderproduct':orderproduct,
    'reviews':reviews,

    }
    return render(request,'store/product_details.html',context)
def submit_review(request,product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        print("Inside Try")
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            print("form except")
            form = ReviewForm(request.POST)
            if form.is_valid():
                print("form validated")
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
