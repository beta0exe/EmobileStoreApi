import time
from gc import get_objects
from django.core.cache import cache
from django.db import models, transaction
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404, redirect
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from store.models import Customer, Product, Category, Order, OrderItem, ProductImage, CartItem, Cart
from store.serializer import (CategorySerializer, ProductSerializer, CustomerSerializer,
                              OrderSerializer,ProductImageSerializer,OrderItemSerializer,CartItemSerializer,CartSerializer)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
from django.utils import timezone
from datetime import timedelta



class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Customer.objects.select_related("user").all()
        elif self.request.user.is_anonymous:
            return None
        else:
            return Customer.objects.select_related("user").filter(user=self.request.user)



class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        cache_key = "category_list"
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = Category.objects.all()
            cache.set(cache_key, queryset,3600)

        return queryset



class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend,SearchFilter, OrderingFilter)
    filterset_fields = ("category", "title")
    search_fields = ('title',)
    ordering_fields = ('title',"unit_price")

    def get_queryset(self):

        cache_key = "product_list"
        queryset = cache.get(cache_key)

        if queryset is None:
             query_set = Product.objects.select_related("category").all()
             cache.set(cache_key, query_set, 3600)
        return queryset

class ProductImageViewSet(viewsets.ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_serializer_context(self):
        return{"product_id":self.kwargs["product_id"]}

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])



class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Order.objects.select_related("customer").filter(customer__user=self.request.user)
        return Order.objects.none()


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(customer__user=self.request.user)

    def perform_create(self, serializer):
        customer, created = Customer.objects.get_or_create(user=self.request.user)
        serializer.save(customer=customer)

    @action(methods=['post'], detail=False, url_path='add_item')
    def add_item(self, request):
        customer = get_object_or_404(Customer, user=self.request.user)
        cart, created = Cart.objects.get_or_create(customer=customer)

        serializer = CartItemSerializer(data=request.data, context={"cart": cart})
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        product = get_object_or_404(Product, id=product_id)
        quantity = serializer.validated_data['quantity']

        if quantity <= 0:
            return Response(
                {"error": "Quantity must be positive"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            cart_item, created = CartItem.objects.select_for_update().get_or_create(
                cart=cart,
                product=product,
                defaults={"quantity": quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()


            if cart_item.quantity > product.inventory:
                return Response(
                    {"error": f"Not enough stock for {product.title}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False, url_path='checkout')
    def checkout(self, request):
        customer = get_object_or_404(Customer, user=self.request.user)

        cart = Cart.objects.filter(customer=customer).first()

        if not cart:
            return Response(
                {"error": "No active cart found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not cart.items.exists():
            return Response(
                {"error": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            for item in cart.items.select_related('product').select_for_update():
                if item.quantity > item.product.inventory:
                    return Response(
                        {"error": f"Not enough stock for {item.product.title}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            order = Order.objects.create(
                customer=customer,
                total=sum(item.product.unit_price * item.quantity for item in cart.items.all()),
                cart=cart
            )

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.unit_price
                )


                Product.objects.filter(pk=item.product.pk).update(
                    inventory=models.F('inventory') - item.quantity
                )
            cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @classmethod
    def clean_old_carts(cls):
        cutoff = timezone.now() - timedelta(days=30)
        Cart.objects.filter(customer__isnull=True, created_at__lt=cutoff).delete()