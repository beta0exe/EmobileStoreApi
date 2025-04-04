from rest_framework import  viewsets
from store.models import Customer, Product, Category, Order, OrderItem, ProductImage, CartItem
from store.serializer import (CategorySerializer, ProductSerializer, CustomerSerializer,
                              OrderSerializer,ProductImageSerializer,OrderItemSerializer,CartItemSerializer,CartSerializer)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
# Create your views here.
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer



class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer



class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend,SearchFilter, OrderingFilter)
    filterset_fields = ("category", "title")
    search_fields = ('title',)
    ordering_fields = ('title',"unit_price")

    def get_queryset(self):
        category_id = self.kwargs.get('category_pk')
        if category_id:
            return Product.objects.filter(category_id=category_id)
        return Product.objects.all()


class ProductImageViewSet(viewsets.ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_serializer_context(self):
        return{"product_id":self.kwargs["product_id"]}

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])



class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer



class CartViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = CartSerializer



class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer