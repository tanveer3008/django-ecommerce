from django.shortcuts import render , redirect,get_object_or_404
from .forms import RegistrationForm,UserForm,UserProfileForm
from .models import Account,UserProfile
from django.contrib import messages,auth
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from orders.models import Order

# verification send mail_subject
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage,send_mail

# assigning user to carts

from carts.views import _cart_id
from carts.models import Cart , CartItem
import requests

# Create your views here.

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']  # in django form we use cleaned datta to get the data from django forms
            username = email.split('@')[0]
            user = Account.objects.create_user(first_name = first_name , last_name = last_name , email = email , username = username , password = password)
            user.phone_number = phone_number
            user.save()

            profile=UserProfile()
            profile.user_id=user.id
            profile.profile_picture='default/admin-logo.png'
            profile.save()

            # user activation -- initially the user is not actyive , once user clicks the link we shared then it will be activated
            current_site = get_current_site(request) # get the cureent site domain
            mail_subject = "Please activate Your Account"
            message = render_to_string('accounts/accounts_verification_email.html',{
                'user':user, # user object
                'domain':current_site, # domain of webpage
                'uid':urlsafe_base64_encode(force_bytes(user.pk)), # encodes the pk for security , in future we will decode the same
                'token':default_token_generator.make_token(user), # generate a token for given user , this will be used for verification
            })
            to_email = email
            #send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email = send_mail(mail_subject,message,from_email='sastidukanshopping@yahoo.com',recipient_list=[to_email])
            #send_email.send()
            #messages.success(request, 'We have Shared Activation link to your Email id, Please click on the link to activate your account.')

            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
    context = {
        'form':form,

    }
    return render(request,'accounts/register.html',context)

def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email = email,password = password)

        if user is not None:
            try:
                cart=Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart = cart).exists()
                if is_cart_item_exists:
                    cart_item=CartItem.objects.filter(cart=cart)

                    # we were facing issue when we add same variation without logging in and then
                    #if we login then it was creating separate entry , below code is to resolve that issue.

                    # here alll variation are getting which are added when we are not logged in
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all() # this comes from cart
                        product_variation.append(list(variation))
                            # here we are getting caarts items of that user
                    cart_item=CartItem.objects.filter(user=user)
                    ex_var_list = []
                    crt_item_id = [] # id of each item in list

                    for item in cart_item:
                        existing_variation = item.variations.all() # this comes from database
                        ex_var_list.append(list(existing_variation))
                        crt_item_id.append(item.id)
                        # checking if the producuct variation is in users cart item
                    for pv in product_variation:
                        if pv in ex_var_list:
                            index = ex_var_list.index(pv)
                            item_id = crt_item_id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                    else:
                        pass
                        """
                        cart_item=CartItem.objects.filter(cart=cart)
                        for item in cart_item:
                            item.user = user
                            item.save()"""

            except:
                pass
            auth.login(request,user)
            messages.success(request,'You are now logged in')
            #return redirect('home')
            # when user is logged in then insted of dashboard user should go to checkout page.
            # this issue was happening because in this function we redirected user to  login_url
            # as a solution we are checking via url if user is coming from chckout page , if yes user will be
            # redirected to checkout page
            url=request.META.get('HTTP_REFERER')
            try:
                print('url',url)
                query=requests.utils.urlparse(url).query
                params=dict(x.split('=') for x in query.split('&'))
                print('params--',params)
                if 'next' in params:
                    nextPage=params['next']
                    return redirect(nextPage)
            #next=cart/checkout
            except:
                return redirect('dashboard')
        else:
            messages.error(request,'Invalid Login Credentials')
            return redirect('login')
    return render(request,'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are now logged out')
    return redirect('login')
    #return redirect('dashboard')

def activate(request,uidb64,token):
    #return  HttpResponse('ok')
    try:
        uid=urlsafe_base64_decode(uidb64).decode() # decoding the uid which we encoded
        user=Account._default_manager.get(pk=uid) # getting user model for that primary SECRET_KEY
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request,'Congratulation , Your Account is activated!!')
        return redirect('login')
    else:
        messages.success(request,'Oopsss! , Activation Link is expired')
        return redirect('register')


@login_required(login_url = 'login') # it is a decorator which we will force you to login if you are not logged in
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    #print(orders)
    orders_count = orders.count()
    context = {
        'orders_count': orders_count,
        'orders':orders,
    }
    return render(request,'accounts/dashboard.html',context)
# my orders in dashboard
def my_orders(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    print(orders)
    context = {
        'orders':orders,
    }
    return render(request,'accounts/my_orders.html',context)

def forgotpassword(request):
    #return HttpResponse('ok')
    if request.method == "POST":
        email = request.POST['email'] # getting email from webpage
        if Account.objects.filter(email=email).exists():
            #if this email is available in accounts # Db
            user=Account.objects.get(email__exact=email) # exact is case sensitive , iexact is case insensitive.
            current_site = get_current_site(request) # get the cureent site domain
            mail_subject = "Link to reset the password"
            message = render_to_string('accounts/reset_password_email.html',{
                'user':user, # user object
                'domain':current_site, # domain of webpage
                'uid':urlsafe_base64_encode(force_bytes(user.pk)), # encodes the pk for security , in future we will decode the same
                'token':default_token_generator.make_token(user), # generate a token for given user , this will be used for verification
            })
            to_email = email
            #send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email = send_mail(mail_subject,message,from_email='sastidukanshopping@yahoo.com',recipient_list=[to_email])
            messages.success(request,'password reset email has been sent to your email address')
            return redirect('login')
        else:
            messages.error(request,'Account does not exists')
            return redirect('forgotpassword')
    return render(request,'accounts/forgetpassword.html')

def resetpasswordvalidate(request,uidb64,token):
    #return HttpResponse('ok')
    try:
        uid=urlsafe_base64_decode(uidb64).decode() # decoding the uid which we encoded
        user=Account._default_manager.get(pk=uid) # getting user model for that primary SECRET_KEY
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']=uid # we saved uid in session in  this step
        messages.success(request,'Please reset your password')
        return redirect('resetpassword')
    else:
        messages.error(request,'Oopsss! , Activation Link is expired')
        return redirect('login')

def resetpassword(request):
    if request.method == "POST":
        password = request.POST['password']
        Confirm_password = request.POST['Confirm_password']

        if password == Confirm_password :
            uid=request.session.get('uid') # getting uid
            print(uid)
            user=Account.objects.get(pk=uid) # gettinf user from primary key
            user.set_password(password)# set password is in built method of django to save the password in hashed format
            user.save() # unless we give this command password will not be updated
            print(password)
            messages.success(request,'password reset is succesful')
            return redirect('login')
        else:
            messages.error(request,'Password do not match')
            return redirect('resetpassword')
    else:
        #return HttpResponse('ok')
        return render(request,'accounts/resetpassword.html')

def edit_profile(request):
    userprofile = get_object_or_404(UserProfile,user=request.user)
    if request.method=='POST':
        user_form=UserForm(request.POST,instance=request.user)
        profile_form=UserProfileForm(request.POST,request.FILES,instance=userprofile) # we neeed to update profile picture also thats why we included request.FILES
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,"Profile update is succesful")
            return redirect('edit_profile')
    else:
        user_form=UserForm(instance=request.user)
        profile_form=UserProfileForm(instance=userprofile)
    context={
        'user_form':user_form,
        'profile_form':profile_form,
        'userprofile':userprofile,
    }

    return render(request,'accounts/edit_profile.html',context)

def tracker(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    #print(orders)
    orders_count = orders.count()
    for order in orders:

        print("order number",order.order_number)
    context = {
        'orders_count': orders_count,
        'orders':orders,
    }

    return render(request,'accounts/tracker.html',context)
