from django.urls import path
from . import views
from django.conf import settings
urlpatterns = [
    path('',views.dashboard,name='dashboard'), # if we go to accout path only then we should redirect to dashboard--http://127.0.0.1:8000/accounts/
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),
    path('forgotpassword/',views.forgotpassword,name='forgotpassword'), # forget password link
    #path('/accounts/resetpasswordvalidate/',views.resetpasswordvalidate,name='resetpasswordvalidate'),
    path('resetpasswordvalidate/<uidb64>/<token>/',views.resetpasswordvalidate, name='resetpasswordvalidate'),
    path('resetpassword/',views.resetpassword,name='resetpassword'),
]
