from django.urls import path
from .views import RegisterView,MyTokenRefreshView,MyTokenObtainPairView,LoginView



urlpatterns = [
    path("register/",RegisterView.as_view(),name="register"),
    path("login/",MyTokenObtainPairView.as_view(),name="login"),
    path("refresh/",MyTokenRefreshView.as_view(),name="refresh"),
    path("logout/",LoginView.as_view(),name="logout"),
]