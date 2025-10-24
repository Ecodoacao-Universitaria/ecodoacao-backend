from django.urls import path
from .views import CadastroUsuarioView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    #url para cadastro de usuário
    path('cadastrar/', CadastroUsuarioView.as_view(), name='cadastrar'),


    #url para autenticação e Refresh
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]