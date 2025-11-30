from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .serializers import CadastroSerializer, DashboardUsuarioSerializer, UsuarioSerializer, MeuPerfilSerializer, AlterarSenhaSerializer, EcoTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from .models import Usuario

Usuario = get_user_model()

# Classe para verificar se o usuário é admin
class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        return is_authenticated and request.user.is_staff

@extend_schema(
    tags=['Autenticação'],
    summary='Obter token JWT',
    description='Retorna um par de tokens (access e refresh) usando usuario e senha',
    request=TokenObtainPairSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "access": {"type": "string", "description": "Token de acesso (expira em 5min)"},
                "refresh": {"type": "string", "description": "Token de refresh (expira em 1 dia)"}
            }
        },
        401: {"description": "Credenciais inválidas"}
    },
    examples=[
        OpenApiExample(
            'Login exemplo',
            value={
                "username": "usuario_teste",
                "password": "senha123"
            },
            request_only=True,
        ),
        OpenApiExample(
            'Resposta sucesso',
            value={
                "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
            },
            response_only=True,
        ),
        OpenApiExample(
            'Resposta falha',
            value={  
                "detail": "No active account found with the given credentials"
            },
            response_only=True,
            status_codes=['401'],
        ),
    ]
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View personalizada para obter tokens JWT.
    Sobrescreve a view padrão para adicionar documentação do Swagger.
    """
    serializer_class = EcoTokenObtainPairSerializer
    pass  # A lógica continua a mesma da classe pai

@extend_schema(
    tags=['Autenticação'],
    summary='Renovar token JWT',
    description='Retorna um novo access token usando um refresh token válido',
    request=TokenRefreshSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "access": {"type": "string", "description": "Novo token de acesso"}
            }
        },
        401: {"description": "Refresh token inválido ou expirado"}
    },
    examples=[
        OpenApiExample(
            'Refresh exemplo',
            value={
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
            },
            request_only=True,
        ),
        OpenApiExample(
            'Resposta sucesso',
            value={
                "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
            },
            response_only=True,
        ),
    ]
)
class CustomTokenRefreshView(TokenRefreshView):
    """
    View personalizada para renovar tokens JWT.
    Sobrescreve a view padrão para adicionar documentação do Swagger.
    """
    pass

@extend_schema(
    tags=['Contas'],
    summary='Cadastrar novo usuário',
    description='Cria um novo usuário no sistema',
    request=CadastroSerializer,
    responses={
        201: UsuarioSerializer,
        400: OpenApiTypes.OBJECT
    }
)
# Cadastro de usuário
class CadastroUsuarioView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = CadastroSerializer
    permission_classes = [AllowAny] 

@extend_schema(
    tags=['Contas'],
    summary='Dashboard do usuário',
    description='Retorna informações do usuário logado (dashboard)',
    responses={
        200: DashboardUsuarioSerializer,
        401: OpenApiTypes.OBJECT
    }
)
# Dashboard do usuário
class DashboardUsuarioView(generics.RetrieveAPIView):
    queryset = Usuario.objects.all()
    serializer_class = DashboardUsuarioSerializer
    permission_classes = [IsAuthenticated]  

    def get_object(self):
        return self.request.user

@extend_schema(
    tags=['Contas'],
    summary='Listar todos os usuários',
    description='Lista todos os usuários do sistema com filtros opcionais (apenas para administradores)',
    parameters=[
        OpenApiParameter(
            name='is_active',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description='Filtrar por usuários ativos (true) ou inativos (false)',
            required=False,
            examples=[
                OpenApiExample('Usuários ativos', value='true'),
                OpenApiExample('Usuários inativos', value='false'),
            ]
        ),
        OpenApiParameter(
            name='is_staff',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description='Filtrar por administradores (true) ou usuários comuns (false)',
            required=False,
            examples=[
                OpenApiExample('Apenas admins', value='true'),
                OpenApiExample('Apenas usuários', value='false'),
            ]
        ),
        OpenApiParameter(
            name='search',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Buscar por username ou email (busca parcial)',
            required=False,
            examples=[
                OpenApiExample('Busca por nome', value='joao'),
                OpenApiExample('Busca por email', value='@gmail.com'),
            ]
        ),
    ],
    responses={
        200: UsuarioSerializer(many=True),
        401: {"description": "Não autenticado"},
        403: {"description": "Sem permissão de administrador"}
    }
)
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
                Q(username__icontains=search) | Q(email__icontains=search)
            )
        
        return queryset.order_by('-date_joined')

@extend_schema(
    tags=['Contas'],
    summary='Deletar usuário',
    description='Deleta um usuário específico pelo ID (apenas para administradores)',
    responses={
        204: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT
    }
)
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

@extend_schema(
    tags=['Contas'],
    summary='Atualizar usuário',
    description='Atualiza informações de um usuário específico pelo ID (apenas para administradores)',
    responses={
        200: UsuarioSerializer,
        400: OpenApiTypes.OBJECT,
        403: OpenApiTypes.OBJECT
    }   
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
    
@extend_schema(
    tags=['Contas'],
    summary='Meu perfil',
    description='Recupera ou atualiza as informações do perfil do usuário autenticado',
    responses={
        200: MeuPerfilSerializer,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT
    }
)
class MeuPerfilView(generics.RetrieveUpdateAPIView):
    serializer_class = MeuPerfilSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # garante que sempre seja o próprio usuário
        return self.request.user

@extend_schema(
    tags=['Contas'],
    summary='Alterar senha',
    description='Permite que o usuário autenticado altere sua senha fornecendo a senha atual e a nova senha',
    request=AlterarSenhaSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT
    }
)
class AlterarSenhaView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AlterarSenhaSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Senha alterada com sucesso."}, status=status.HTTP_200_OK)