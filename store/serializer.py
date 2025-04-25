from itertools import product

from rest_framework import  serializers

from store.models import Category, Product,ProductStorage,ProductColors, Order, Customer,OrderItem,CartItem,ProductImage,Cart,Address


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
        return Product.objects.create(product_id = product_id,**validated_data)

class ProductStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStorage
        fields = ["size"]

class ProductColorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColors
        fields = ["color"]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True)
    colors = ProductColorsSerializer(many=True)
    storage = ProductStorageSerializer(many=True)
    category = CategorySerializer()
    class Meta:
        model = Product
        fields = ["id","brand","title","description","storage"
            ,"colors","cpu","cores","main_camera","front_camera"
            ,"battery_capacity","delivery_info","is_active","warranty"
            ,"screen_resolution","screen_refresh_rate","screen_size","pixel_density","unit_price",
                  "inventory","last_update","category","images"]
        read_only_fields = ("id","last_update")

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        colors_data = validated_data.pop("colors", [])
        storage_data = validated_data.pop("storage", [])
        category_data = validated_data.pop("category", None)

        if category_data is None:
            raise serializers.ValidationError({"category": "This field is required."})

        category, _ = Category.objects.get_or_create(title=category_data["title"])
        product = Product.objects.create(category=category, **validated_data)

        for image in images_data:
            ProductImage.objects.create(product=product, **image)

        for color in colors_data:
            ProductColors.objects.create(product=product, **color)

        for storage in storage_data:
            ProductStorage.objects.create(product=product, **storage)

        return product


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ["id","product","quantity","unit_price"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True,read_only=True)
    class Meta:
        model = Order
        fields = ["id","payment_status","placed_at","customer","items","total"]
        read_only_fields = ("id","payment_status","total")

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity"]

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Product does not exist or is unavailable.")
        return value

    def validate_quantity(self, value):
       if value < 1:
           raise serializers.ValidationError({"quantity": "This quantity cannot be less than 1"})
       return value



class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True,read_only=True)
    id = serializers.CharField(read_only=True)
    class Meta:
        model = Cart
        fields = ["id","created_at","items"]
        read_only_fields = ["created_at"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id","street","city"]



class CustomerSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=True,read_only=True)
    class Meta:
        model = Customer
        fields = ["id","name","phone","email","address"]