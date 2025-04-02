from django.contrib import admin

from store.models import Customer, Product, ProductImage, Category, Order


# Register your models here.


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id","name", "email")
    list_per_page = 10
    ordering = ("id",)



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id","title", "unit_price"]
    list_per_page = 10
    ordering = ("id",)



@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["id","image"]
    list_per_page = 10
    ordering = ("id",)



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id","title"]
    list_per_page = 10
    ordering = ("id",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id","payment_status","placed_at","customer"]
    list_per_page = 10
    ordering = ("id",)







