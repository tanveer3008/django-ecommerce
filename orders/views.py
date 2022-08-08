from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order,Payment,OrderProduct
from store.models import Product
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.conf import settings
import json
from django.core.mail import EmailMessage,send_mail
from django.template.loader import render_to_string

def place_order(request,total=0,quantity=0):
    current_user=request.user
    # if cart count is less than 0 then redirect to store page.
    cart_items=CartItem.objects.filter(user=current_user)
    cart_count=cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    tax=0
    grand_total=0

    for cart_item in cart_items:
        total +=(cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax=(2*total)/100
    grand_total=total + tax
    dollar_amount=round(grand_total/76.84,2)

    if request.method == 'POST':
        #print('inside post method')
        form = OrderForm(request.POST)
        #print(form.errors)
        if form.is_valid():
            print("inside form vaalidation")
            data=Order()
            data.user=current_user
            data.first_name=form.cleaned_data['first_name']
            data.last_name=form.cleaned_data['last_name']
            data.phone=form.cleaned_data['phone']
            data.email=form.cleaned_data['email']
            data.address_line_1=form.cleaned_data['address_line_1']
            data.address_line_2=form.cleaned_data['address_line_2']
            data.country=form.cleaned_data['country']
            data.state=form.cleaned_data['state']
            data.city=form.cleaned_data['city']
            data.order_note=form.cleaned_data['order_note']
            data.order_total=grand_total
            data.tax=tax
            data.ip=request.META.get('REMOTE_ADDR')
            print(data.ip)
            data.save()
            # printing details in payment page
            #generate order number
            yr=int(datetime.date.today().strftime('%Y'))
            mr=int(datetime.date.today().strftime('%m'))
            dt=int(datetime.date.today().strftime('%d'))
            d=datetime.date(yr,mr,dt)
            current_date = d.strftime("%Y%m%d")#20220722
            order_number=current_date + str(data.id) # if firstorder of 2022 july 22 then 2022072201
            data.order_number=order_number
            data.save()
            """
            currency = 'INR'
            amount = int(grand_total)*100  # Rs. 200
            print(amount)

            # authorize razorpay client with API Keys.
            razorpay_client = razorpay.Client(
            auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            # Create a Razorpay Order
            razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                               currency=currency,
                                                               payment_capture='1'))

            # order id of newly created order.
            razorpay_order_id = razorpay_order['id']
            callback_url = 'paymenthandler/'
            """
            # we need to pass these details to frontend.
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            print(order)
            dollar_amount=round(grand_total/76.84,2)
            context= {
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
                'dollar_amount':dollar_amount
            }
            """
            context['razorpay_order_id'] = razorpay_order_id
            context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
            context['razorpay_amount'] = amount
            context['currency'] = currency
            context['callback_url'] = callback_url
            """
            return render(request,'orders/payments.html',context)

        else:
            print('else block')
            return redirect('checkout')


def payments(request):
    body = json.loads(request.body)
    current_user=request.user
    order = Order.objects.get(user=current_user, is_ordered=False,order_number=body['orderID'])
    #dollar_amount=round(order.order_total/76.84,2)

    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        #amount_paid_dollar = dollar_amount,
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()
     # move the cart items into order product table
    #return render(request,'orders/payments.html')
    cart_items=CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()
     # to get data in many to many fields we first need to save the object and then access the fields
     # in our case variations
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()
        if item.product_id is not None:

            print('product_id:',item.product_id)
        else:
            print('null')

     #reduce the quantity
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # clear carts
    CartItem.objects.filter(user=request.user).delete()
    #  send order received EmailField
    mail_subject = "Thank You for Your Order"
    message = render_to_string('orders/order_received_email.html',{
        'user':request.user, # user object
        'order':order,
    })
    to_email = request.user.email
    #send_email = EmailMessage(mail_subject,message,to=[to_email])
    send_email = send_mail(mail_subject,message,from_email='sastidukanshopping@gmail.com',recipient_list=[to_email])
     # send json data to javasacript function in paypal
    data = {
     'order_number':order.order_number,
     'transID': payment.payment_id,
     }
    return JsonResponse(data) # returning data from which it came , means send data function

    #return render(request,'orders/payments.html')

"""
@csrf_exempt
def paymenthandler(request):

    # only accept POST request.
    if request.method == "POST":
        try:

            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            print('paymentid:',payment_id)
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            print('signature:',signature)
            print('razorpay_order_id:',razorpay_order_id)
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is None:
                amount = grand_total  # Rs. 200
                try:

                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)

                    # render success page on successful caputre of payment

                except:

                    # if we don't find the required parameters in POST data
                     return HttpResponseBadRequest()
            else:
                    # if other than POST request is made.
                return HttpResponseBadRequest()
        except:
            pass
# Create your views here.

"""

def order_complete(request):
    order_number=request.GET.get('order_number')
    transID=request.GET.get('payment_id')
    subtotal =0
    try:
        order=Order.objects.get(order_number=order_number,is_ordered=True)
        #print(list(order))
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        #print(order.id)
        #print(ordered_products)
        for i in ordered_products:

            subtotal += i.product_price*i.quantity
        payment=Payment.objects.get(payment_id=transID)

        context = {
        'order':order,
        'ordered_products': ordered_products,
        'order_number':order.order_number,
        'transID':payment.payment_id,
        'payment':payment,
        'subtotal':subtotal

        }
        return render(request,'orders/order_complete.html',context)
    except(Payment.DoesNotExist,Order.DoesNotExist):
        return redirect('home')
