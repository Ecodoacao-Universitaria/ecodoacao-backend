from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from .serializers import CadastroSerializer, DashboardUsuarioSerializer, UsuarioSerializer
from .models import Usuario
import os


# Classe para verificar se o usuário é admin
class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        return is_authenticated and request.user.is_staff


# Create your views here.

#cadastro de usuário
class CadastroUsuarioView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = CadastroSerializer
    permission_classes = [AllowAny] #permite que qualquer pessoa possa acessar essa view para se cadastrar



@api_view(['GET'])
@permission_classes([AllowAny])
def criar_superuser_temporario(request):
  
    try:
        user_model = get_user_model()
        
        # Lendo as variáveis de ambiente que você configurou
        ADMIN_USERNAME = os.getenv('ADMIN_USER')
        ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
        ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

        # Se qualquer uma estiver faltando, falhe com uma mensagem clara
        if not all([ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD]):
            return Response(
                {"erro": "Uma ou mais variáveis (ADMIN_USER, ADMIN_EMAIL, ADMIN_PASSWORD) não foram configuradas no Render."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        
        if not user_model.objects.filter(username=ADMIN_USERNAME).exists():
            
            # Tenta criar o superusuário
            user_model.objects.create_superuser(
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                password=ADMIN_PASSWORD
            )
            return Response(
                {"sucesso": f"Usuário '{ADMIN_USERNAME}' criado com sucesso."}, 
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"mensagem": f"Usuário '{ADMIN_USERNAME}' já existe."}, 
                status=status.HTTP_200_OK
            )
            
    except Exception as e:
        # Captura qualquer exceção que ocorra durante o processo
        return Response(
            {"erro_real_capturado_pelo_django": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    


class DashboardUsuarioView(generics.RetrieveAPIView):
    queryset = Usuario.objects.all()
    serializer_class = DashboardUsuarioSerializer
    permission_classes = [IsAuthenticated]  # Apenas usuários autenticados podem acessar esta view

    def get_object(self):
        # Retorna o usuário logado
        return self.request.user


# Lista todos os usuários (apenas admin)
class ListarUsuariosView(generics.ListAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAdmin]
    
    def get_queryset(self):
        """
        Permite filtrar por is_active e is_staff se fornecido nos query params
        """
        queryset = super().get_queryset()
        
        # Filtro por status ativo/inativo
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        # Filtro por role (admin/usuario)
        is_staff = self.request.query_params.get('is_staff', None)
        if is_staff is not None:
            is_staff_bool = is_staff.lower() == 'true'
            queryset = queryset.filter(is_staff=is_staff_bool)
        
        # Busca por username ou email
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                username__icontains=search
            ) | queryset.filter(
                email__icontains=search
            )
        
        return queryset.order_by('-date_joined')


# Deletar usuário (apenas admin)
class DeletarUsuarioView(generics.DestroyAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'id'
    
    def destroy(self, request, *args, **kwargs):
        usuario = self.get_object()
        
        # Evitar que um admin delete a si mesmo
        if usuario == request.user:
            return Response(
                {"erro": "Você não pode deletar sua própria conta."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Evitar que um admin delete outro admin (apenas superuser pode)
        if usuario.is_staff and not request.user.is_superuser:
            return Response(
                {"erro": "Apenas superusuários podem deletar contas de administrador."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        username_deletado = usuario.username
        usuario.delete()
        
        return Response(
            {"sucesso": f"Usuário '{username_deletado}' deletado com sucesso."},
            status=status.HTTP_204_NO_CONTENT
        )


# Atualizar usuário (promover/rebaixar ou desativar) - apenas admin
class AtualizarUsuarioView(generics.UpdateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'id'
    http_method_names = ['patch']  # Apenas PATCH, não PUT
    
    def patch(self, request, *args, **kwargs):
        usuario = self.get_object()
        
        # Evitar que um admin altere a si mesmo (para is_staff)
        if 'is_staff' in request.data and usuario == request.user:
            return Response(
                {"erro": "Você não pode alterar seu próprio status de administrador."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Apenas superuser pode alterar status de admin
        if 'is_staff' in request.data and usuario.is_staff and not request.user.is_superuser:
            return Response(
                {"erro": "Apenas superusuários podem alterar o status de administradores."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().patch(request, *args, **kwargs)