from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminDoacoesPendentesView,
    CriarDoacaoView, 
    AdminAtualizarDoacaoView, 
    HistoricoDoacoesView,
    AdminBadgeViewSet,
    ListarTiposDoacaoView
)
from . import views

router = DefaultRouter()
router.register(r'badges', views.BadgeViewSet, basename='badge')
admin_router = DefaultRouter()
admin_router.register(r'admin/badges', AdminBadgeViewSet, basename='admin-badge')

urlpatterns = [
    # Rota para Listar Doações Pendentes (Admin)
    path('admin/pendentes/', AdminDoacoesPendentesView.as_view(),
            name='admin_doacoes_pendentes'),

    # Rota para Submeter Doação
    path('submeter/', CriarDoacaoView.as_view(), name='doacao_submeter'),
    
    # Rota para Validar Doação
    # <int:pk> significa que a URL vai ser ex: /api/doacoes/admin/validar/1/
    path('admin/validar/<int:pk>/', AdminAtualizarDoacaoView.as_view(), name='admin_doacao_validar'),

    # Rota para o Histórico do Usuário
    path('historico/', HistoricoDoacoesView.as_view(), name='doacao_historico'),

    # Tipos de Doação
    path('tipos/', ListarTiposDoacaoView.as_view(), name='doacao_tipos'),

    path('', include(router.urls)),
    path('', include(admin_router.urls))
]