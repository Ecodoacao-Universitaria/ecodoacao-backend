from django.urls import path
from .views import (
    AdminDoacoesPendentesView,
    CriarDoacaoView, 
    AdminAtualizarDoacaoView, 
    HistoricoDoacoesView 
)

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
]