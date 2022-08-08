from django.contrib import admin
from.models import Payment,Order,OrderProduct

# Register your models here.
# this class is used to show order product details inlined in order model
class OrderProductInline(admin.TabularInline):
    model=OrderProduct
    readonly_fields = ('payment','user','product','quantity','product_price','ordered')
    extra=0

class OrderAdmin(admin.ModelAdmin):
    list_display=['order_number','full_name','phone','email','city','order_total','ip','is_ordered']
    #list_filter=['status','is_ordered']
    search_fields=['order_number','phone','email','first_name']
    list_per_page= 20
    inlines=[OrderProductInline]
admin.site.register(Payment)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderProduct)
