from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from integration.core.views import clientes, contratos, despesas, emprestimos, lojas 
from integration.core.views.resources import promotoras 

router = DefaultRouter()

router.register(r'clientes', clientes.ClientesViewSet, basename='clientes')
router.register(r'contratos', contratos.ContratosViewSet, basename='contratos')
router.register(r'despesas', despesas.DespesasViewSet, basename='despesas')
router.register(r'emprestimos', emprestimos.EmprestimosViewSet, basename='emprestimos')
router.register(r'lojas', lojas.LojasViewSet, basename='lojas')
router.register(r'promotoras', promotoras.PromotorasViewSet, basename='promotoras')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),
    path('integration/', include(router.urls)),
    path('integration/', include(('integration.users.routers', 'users'), namespace='users-api')),
    path('integration/', include(('integration.auth.routers', 'auth'), namespace='auth-api')),
]

