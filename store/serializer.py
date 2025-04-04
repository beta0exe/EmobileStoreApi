from itertools import product

from rest_framework import  serializers

from store.models import Category, Product, Order, Customer,OrderItem,CartItem,ProductImage,Cart,Address


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id","title"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id","image"]

    def create(self, validated_data):
        product_id =self.context["product_id"]
        Product.objects.create(product_id = product_id,**validated_data)


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True)
    class Meta:
        model = Product
        fields = ["id","title","description","unit_price","inventory","last_update","category","images"]
        read_only_fields = ("id","last_update")

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id","product","quantity","unit_price"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True,read_only=True)
    class Meta:
        model = Order
        fields = ["id","payment_status","placed_at","customer","items"]

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id","product","quantity"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True,read_only=True)
    class Meta:
        model = Cart
        fields = ["id","created_at","items"]
        read_only_fields = ("id","created_at")


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id","street","city"]



class CustomerSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=True,read_only=True)
    class Meta:
        model = Customer
        fields = ["id","name","phone","email","address"]