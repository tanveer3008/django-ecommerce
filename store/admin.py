from django.contrib import admin
from .models import Product,Variation,ReviewRating #.models reporesent models.py of current dir
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('Product_name',)}
    list_display = ['Product_name','slug','price','stock','category','is_available']

class VariationAdmin(admin.ModelAdmin):
    list_display = ['product','variation_category','variation_value','is_active','created_date'] # things which will mbe displayed when we open this model
    list_editable = ('is_active',) #  making is_active field editable
    list_filter = ['product','variation_category','variation_value','is_active','created_date'] # filter panel at lhs side
admin.site.register(Product,ProductAdmin)
admin.site.register(Variation,VariationAdmin)
admin.site.register(ReviewRating)


# Register your models here.
