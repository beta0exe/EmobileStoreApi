import uuid

from django.conf import settings
from django.db import models
from core.models import User


# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=100)
    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory = models.IntegerField()
    last_update = models.DateTimeField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    def __str__(self):
        return self.title


class ProductImage(models.Model):
    image = models.ImageField(upload_to="images/")
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

class Order(models.Model):
    payment_status =[
        ("S","Successful"),
        ("P","Pending"),
        ("F","Failed"),
    ]
    placed_at = models.DateTimeField()
    payment_status = models.CharField(max_length=1,choices=payment_status,default="P")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)



class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
