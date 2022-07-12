from django.contrib import admin
from .models import Product #.models reporesent models.py of current dir
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('Product_name',)}
    list_display = ['Product_name','slug','price','stock','category','is_available']


admin.site.register(Product,ProductAdmin)


# Register your models here.
