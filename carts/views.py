

from django.shortcuts import render,redirect,get_object_or_404
from .models import Cart
from .models import CartItem
from store.models import Product,Variation
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
# Create your views here.
#cart = request.session.session_key
def _cart_id(request):
    #cart = request.session.session_key
    cart=request.session.session_key
    print(cart)
    #cart = request.session.get(CART_SESSION_ID)
    if not cart:
        cart = request.session.create()
    return cart
def add_cart(request,product_id):
    #global cart
    current_user = request.user
    product = Product.objects.get(id=product_id) # get the product_id
    if current_user.is_authenticated:
            product_variation = []
            if request.method == 'POST':
                for item in request.POST:
                    key = item
                    value=request.POST[key]
                    #return HttpResponse("tanveer")
                    #print(key ,value)
                    #exit()
                    try:
                        variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                        #print (variation)
                        #exit()
                        product_variation.append(variation)
                    except:
                        pass

            is_cart_item_exists = CartItem.objects.filter(product = product , user =current_user).exists()

            if is_cart_item_exists:
                cart_item = CartItem.objects.filter(product=product, user =current_user)
                # we will check if there is existing variation available , if yes then we will append that
                # else new cart item will be created_date

                ex_var_list = []
                crt_item_id = [] # id of each item in list

                for item in cart_item:
                    existing_variation = item.variations.all() # this comes from database
                    ex_var_list.append(list(existing_variation))
                    crt_item_id.append(item.id)
                #print(ex_var_list)

                if product_variation in ex_var_list:

                    index = ex_var_list.index(product_variation)
                    item_id = crt_item_id[index]
                    item = CartItem.objects.get(product=product, id=item_id)
                    item.quantity+=1
                    item.save()
                    #return HttpResponse('True')
                else:
                    item = CartItem.objects.create(product=product,quantity=1,user =current_user)
                    #return HttpResponse('false')
                    #exit()
                    if len(product_variation) > 0:
                        item.variations.clear()
                        item.variations.add(*product_variation)
                    #cart_item.quantity +=1
                    item.save()
            else:
                #cart = Cart.objects.get(cart_id = _cart_id(request))
                cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
                )
                if len(product_variation) > 0:
                    item = CartItem.objects.create(product=product,quantity=1,cart=cart)
                    item.variations.clear()
                    cart_item.variations.add(*product_variation)
                    item.save()
            return redirect('cart')
        # if the user is not authenticated
    else:

        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value=request.POST[key]
                #return HttpResponse("tanveer")
                #print(key ,value)
                #exit()
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    #print (variation)
                    #exit()
                    product_variation.append(variation)
                except:
                    pass
        try:
            cart = Cart.objects.get(cart_id = _cart_id(request))
        except ObjectDoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        #cart = Cart.objects.get(cart_id=_cart_id(request))
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product = product , cart = cart).exists()

        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            # we will check if there is existing variation available , if yes then we will append that
            # else new cart item will be created_date

            ex_var_list = []
            crt_item_id = [] # id of each item in list

            for item in cart_item:
                existing_variation = item.variations.all() # this comes from database
                ex_var_list.append(list(existing_variation))
                crt_item_id.append(item.id)
            print(ex_var_list)

            if product_variation in ex_var_list:

                index = ex_var_list.index(product_variation)
                item_id = crt_item_id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity+=1
                item.save()
                #return HttpResponse('True')
            else:
                item = CartItem.objects.create(product=product,quantity=1,cart=cart)
                #return HttpResponse('false')
                #exit()
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                #cart_item.quantity +=1
                item.save()
        else:
            cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
            )
            if len(product_variation) > 0:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                item = CartItem.objects.create(product=product,quantity=1,cart=cart)
                item.variations.clear()
                cart_item.variations.add(*product_variation)
                item.save()
        return redirect('cart')
def remove_cart(request,product_id,cart_item_id):
    product = Product.objects.get(id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user , id = cart_item_id)
        else:
            cart = Cart.objects.get(cart_id= _cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart , id = cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')
def remove_cart_item(request,product_id,cart_item_id):
    product = Product.objects.get(id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user , id = cart_item_id)
    else:
        cart = Cart.objects.get(cart_id= _cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart , id = cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request,total=0,quantity = 0 ,cart_items=None ):
    tax=0
    grand_total=0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user , is_active = True)
        else:
            cart = Cart.objects.get(cart_id= _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart , is_active = True)
        for cart_item in cart_items:
            total +=(cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax=(2*total)/100
        grand_total=total + tax
    except:
        pass
    context = {
    'total'      : total ,
    'quantity'   : quantity,
    'cart_items' : cart_items,
    'tax'        : tax,
    'grand_total': grand_total,

    }
    return render(request,'store/carts.html',context)

# checkout functyion
@login_required(login_url = 'login')
def checkout(request,total=0,quantity = 0 ,cart_items=None):
    #return HttpResponse('ok')
    # added same code as of cart function
    tax=0
    grand_total=0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user , is_active = True)
        else:
            cart = Cart.objects.get(cart_id= _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart , is_active = True)    

        for cart_item in cart_items:
            total +=(cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax=(2*total)/100
        grand_total=total + tax
    except:
        pass
    context = {
    'total'      : total ,
    'quantity'   : quantity,
    'cart_items' : cart_items,
    'tax'        : tax,
    'grand_total': grand_total,

    }
    return render(request,'store/checkout.html',context)
