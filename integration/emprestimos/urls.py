# from django.urls import path
# from integration.emprestimos.views import emprestimos

# app_name = 'emprestimos'

# urlpatterns = [
#     path('', emprestimos.EmprestimosViewSet, name='emprestimos'),    
# ]


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from integration.emprestimos.views import emprestimos

app_name = 'emprestimos'

router = DefaultRouter()
router.register('', emprestimos.EmprestimosViewSet, basename='emprestimos')

urlpatterns = [
    path('', include(router.urls)),
]