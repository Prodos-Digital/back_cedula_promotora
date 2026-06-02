from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from integration.core import db_backup_views
from integration.core.views import clientes, contratos, despesas, lojas, pre_contratos, futuros_contratos 
from integration.core.views.resources import promotoras, convenios, bancos, corretores, operacoes, natureza_despesa, canal_aquisicao_clientes 

router = DefaultRouter()

router.register(r'clientes', clientes.ClientesViewSet, basename='clientes')
router.register(r'contratos', contratos.ContratosViewSet, basename='contratos')
router.register(r'despesas', despesas.DespesasViewSet, basename='despesas')
router.register(r'lojas', lojas.LojasViewSet, basename='lojas')
router.register(r'pre-contratos', pre_contratos.PreContratosViewSet, basename='pre-contratos')
router.register(r'resources/promotoras', promotoras.PromotorasViewSet, basename='promotoras')
router.register(r'resources/convenios', convenios.ConveniosViewSet, basename='convenios')
router.register(r'resources/bancos', bancos.BancosViewSet, basename='bancos')
router.register(r'resources/corretores', corretores.CorretoresViewSet, basename='corretores')
router.register(r'resources/operacoes', operacoes.OperacoesViewSet, basename='operacoes')
router.register(r'resources/natureza-despesas', natureza_despesa.NaturezaDespesasViewSet, basename='natureza-despesas')
router.register(r'resources/canal-aquisicao-clientes', canal_aquisicao_clientes.CanalAquisicaoClienteViewSet, basename='canal-aquisicao-clientes')
router.register(r'futuros-contratos', futuros_contratos.FuturoContratoViewSet, basename='futuros-contratos')

urlpatterns = [
    path(
        'admin/tools/db-dump/',
        admin.site.admin_view(db_backup_views.admin_database_dump),
        name='admin_db_dump',
    ),
    path(
        'admin/tools/db-restore/',
        admin.site.admin_view(db_backup_views.admin_database_restore),
        name='admin_db_restore',
    ),
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),
    path('integration/', include(router.urls)),
    path('integration/', include(('integration.users.routers', 'users'), namespace='users-api')),
    path('integration/', include(('integration.auth.routers', 'auth'), namespace='auth-api')),   
    path('integration/emprestimos/', include('integration.emprestimos.urls', 'emprestimos')),

]

