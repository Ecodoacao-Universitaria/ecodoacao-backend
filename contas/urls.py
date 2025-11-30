from django.urls import path
from .views import (
    CadastroUsuarioView, 
    criar_superuser_temporario, 
    DashboardUsuarioView,
    ListarUsuariosView,
    DeletarUsuarioView,
    AtualizarUsuarioView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    MeuPerfilView, 
    AlterarSenhaView
)

urlpatterns = [
    #url para cadastro de usuário
    path('cadastrar/', CadastroUsuarioView.as_view(), name='cadastrar'),

    #url para autenticação e Refresh (LOGIN)
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

    #url temporária para criar superusuário na produção
    path('criar-superuser-temporario/', criar_superuser_temporario, name='criar_superuser_temporario'),

    #url para o dashboard do usuário
    path('dashboard/', DashboardUsuarioView.as_view(), name='dashboard'),
    
    # Nova rota para listar todos os usuários (apenas admin)
    path('usuarios/', ListarUsuariosView.as_view(), name='listar-usuarios'),
    
    # Nova rota para deletar usuário (apenas admin)
    path('usuarios/<int:id>/deletar/', DeletarUsuarioView.as_view(), name='deletar-usuario'),
    
    # Nova rota para atualizar usuário (apenas admin)
    path('usuarios/<int:id>/atualizar/', AtualizarUsuarioView.as_view(), name='atualizar-usuario'),
    # Rotas para meu perfil e alterar senha
    path('usuarios/meu-perfil/', MeuPerfilView.as_view(), name='meu-perfil'),
    path('usuarios/alterar-senha/', AlterarSenhaView.as_view(), name='alterar-senha'),
]