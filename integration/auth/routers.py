from rest_framework.routers import SimpleRouter
from integration.auth.views import LoginViewSet, RegistrationViewSet

from django.urls import path, re_path
from django.contrib.auth import views as r_views

external_routes = SimpleRouter()

external_routes.register(r'auth/login', LoginViewSet, basename='auth-login')
external_routes.register(r'auth/register', RegistrationViewSet, basename='auth-register')

urlpatterns = [
    *external_routes.urls,
]
