import uuid
from msilib.schema import Property

from django.conf import settings
from django.db import models
from core.models import User


# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Product(models.Model):
    brand = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    screen_size = models.DecimalField(max_digits=10, decimal_places=2)
    cpu = models.CharField(max_length=100)
    cores = models.IntegerField()
    main_camera = models.CharField(max_length=100)
    front_camera = models.CharField(max_length=100)
    battery_capacity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    delivery_info = models.CharField(max_length=100)
    warranty = models.CharField(max_length=100)
    screen_resolution = models.CharField(max_length=100)
    screen_refresh_rate = models.IntegerField()
    pixel_density = models.IntegerField()
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class ProductColors(models.Model):
    color = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='colors')

    def __str__(self):
        return self.color

class ProductStorage(models.Model):
    StorageChoices = [
        ("128GB", "128GB"),
        ("256GB", "256GB"),
        ("512GB", "512GB"),
        ("1TB", "1TB"),
    ]
    size = models.CharField(max_length=10,choices=StorageChoices,default="128GB")
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name="storage")

    def __str__(self):
        return self.size

class ProductImage(models.Model):
    image = models.URLField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name="images")

class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.IntegerField()

    def __str__(self):
        return self.name

class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)



class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    @property
    def totals(self):
        return sum(item.total for item in self.items.all())

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name="items")
    quantity = models.PositiveIntegerField()

    @property
    def total(self):
        return self.quantity * self.product.unit_price

class Order(models.Model):
    payment_status =[
        ("S","Successful"),
        ("P","Pending"),
        ("F","Failed"),
    ]
    cart = models.ForeignKey(Cart, on_delete=models.PROTECT,related_name="order")
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=1,choices=payment_status,default="P")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=10, decimal_places=2)

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name="items")
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total(self):
        return self.quantity * self.unit_price