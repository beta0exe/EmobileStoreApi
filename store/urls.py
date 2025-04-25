from itertools import product

from rest_framework_nested import  routers

from store.views import ProductViewSet, OrderViewSet, CustomerViewSet, CategoryViewSet, CartViewSet,ProductImageViewSet

router = routers.DefaultRouter()
router.register(r'products', ProductViewSet, 'product')
router.register(r'orders', OrderViewSet, 'order')
router.register(r"categories",CategoryViewSet, "category")
router.register(r'customers',CustomerViewSet, "customer")
router.register(r"cart",CartViewSet, "cart")



product_routers = routers.NestedSimpleRouter(router, r'products', lookup='product')
product_routers.register("images",ProductImageViewSet, "image")


category_routers = routers.NestedSimpleRouter(router, r'categories', lookup='category')
category_routers.register(r'products', ProductViewSet, basename='category-products')


urlpatterns = [] +router.urls + product_routers.urls + category_routers.urls