from django.contrib import admin
from .models import Category #.models reporesent models.py of current dir
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('Category_name',)}
    list_display = ['Category_name','slug']


admin.site.register(Category,CategoryAdmin)
