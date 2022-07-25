from django.db import models
from category.models import Category
from django.urls import reverse
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
    modified_date = models.DateTimeField(auto_now = True)

    def get_url(self):
        return reverse('product_detail',args = [self.category.slug , self.slug])


    def __str__(self):
        return self.Product_name



variation_category_list = (

('color','color'),
('size','size'),
)
class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category = 'color',is_active=True)


    def sizes(self):
        return super(VariationManager,self).filter(variation_category = 'size',is_active=True)


class Variation(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100,choices=variation_category_list)
    variation_value =  models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add = True)

    objects = VariationManager()

    def __str__(self): # as product is not str thats why we used unicode
        return self.variation_value
