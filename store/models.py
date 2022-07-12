from django.db import models
from category.models import Category
# Create your models here.

class Product(models.Model):
    Product_name = models.CharField(max_length = 250,unique = True)
    slug = models.SlugField(max_length = 250,unique = True) # url of the category
    description =  models.CharField(max_length = 250,blank = True)
    price =  models.IntegerField()
    image = models.ImageField(upload_to='photos/product',blank = True)
    stock =  models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add = True)
    created_date = models.DateTimeField(auto_now = True)

    #class Meta:
        #verbose_name = 'category'
        #verbose_name_plural = 'categories'

    def __str__(self):
        return self.Product_name
