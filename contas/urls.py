from django.urls import path
from .views import CadastroUsuarioView, criar_superuser_temporario, DashboardUsuarioView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    #url para cadastro de usuário
    path('cadastrar/', CadastroUsuarioView.as_view(), name='cadastrar'),


    #url para autenticação e Refresh
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    #url temporária para criar superusuário na produção
    path('criar-superuser-temporario/', criar_superuser_temporario, name='criar_superuser_temporario'),

    #url para o dashboard do usuário
    path('dashboard/', DashboardUsuarioView.as_view(), name='dashboard'),
]