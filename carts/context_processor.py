from .models import Cart,CartItem
from .views import _cart_id

def counter(request):
    carts_count = 0
    if 'admin' in request.path:
        return []
    else:
        try:
            cart = Cart.objects.filter(cart_id = _cart_id(request))
            if request.user.is_authenticated: # if we login as user then cart count should be increased
                cart_items = CartItem.objects.all().filter(user = request.user)
            else:
                cart_items = CartItem.objects.all().filter(cart = cart[:1])
            for cart_item in cart_items:
                carts_count += cart_item.quantity
        except:
            carts_count = 0
    return dict(carts_count=carts_count)
