

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from integration.emprestimos.views import emprestimos, clientes, parcelas, acordos, acordo_parcelas

app_name = 'emprestimos'

router = DefaultRouter()
router.register(r'emprestimos', emprestimos.EmprestimosViewSet, basename='emprestimos')
router.register(r'parcelas', parcelas.EmprestimoParcelasViewSet, basename='parcelas')
router.register(r'clientes', clientes.ClientesViewSet, basename='clientes')
router.register(r'acordos', acordos.AcordosViewSet, basename='acordos')
router.register(r'parcelas-acordo', acordo_parcelas.AcordoParcelasViewSet, basename='parcelas-acordo')


urlpatterns = [
    path('', include(router.urls)),
]

