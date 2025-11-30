from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Doacao, Badge, UsuarioBadge, TipoDoacao
from .serializers import (
    DoacaoSerializer, 
    CriarDoacaoSerializer, 
    ValidarDoacaoSerializer,
    BadgeSerializer,
    UsuarioBadgeSerializer,
    ComprarBadgeSerializer,
    DashboardUsuarioSerializer,
    TipoDoacaoSerializer,
)
from .services import BadgeService

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

# ============================================================================
# TIPOS DE DOAÇÃO
# ============================================================================

@extend_schema(tags=['Doações'], summary='Listar tipos de doação')
class ListarTiposDoacaoView(generics.ListAPIView):
    queryset = TipoDoacao.objects.all().order_by('nome')
    serializer_class = TipoDoacaoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

# ============================================================================
# DOAÇÕES
# ============================================================================

@extend_schema(tags=['Doações'], summary='Criar doação')
class CriarDoacaoView(generics.CreateAPIView):
    serializer_class = CriarDoacaoSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

@extend_schema(tags=['Doações'], summary='Histórico de doações do usuário')
class HistoricoDoacoesView(generics.ListAPIView):
    serializer_class = DoacaoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        queryset = Doacao.objects.filter(doador=user).select_related(
            'tipo_doacao', 'validado_por'
        ).order_by('-data_submissao')
        
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param.upper())
        
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

# ============================================================================
# ADMIN
# ============================================================================

@extend_schema(tags=['Admin'], summary='Listar doações pendentes')
class AdminDoacoesPendentesView(generics.ListAPIView):
    serializer_class = DoacaoSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Doacao.objects.filter(status='PENDENTE').select_related(
            'doador', 'tipo_doacao'
        ).order_by('-data_submissao')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

@extend_schema(tags=['Admin'], summary='Validar doação')
class AdminAtualizarDoacaoView(generics.UpdateAPIView):
    queryset = Doacao.objects.all()
    serializer_class = ValidarDoacaoSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        doacao = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        novo_status = serializer.validated_data['status']
        motivo_recusa = serializer.validated_data.get('motivo_recusa')

        if novo_status == 'APROVADA':
            doacao.aprovar(request.user)
            BadgeService.premiar_doacao_aprovada(doacao)
            resultado = {'sucesso': True, 'mensagem': 'Doação aprovada com sucesso.'}
        else:
            doacao.recusar(request.user, motivo_recusa)
            resultado = {'sucesso': True, 'mensagem': 'Doação recusada.'}

        return Response(resultado, status=status.HTTP_200_OK)

# ============================================================================
# BADGES
# ============================================================================

@extend_schema(tags=['Admin'])
class AdminBadgeViewSet(viewsets.ModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

@extend_schema(tags=['Badges'])
class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Badge.objects.filter(ativo=True)
    serializer_class = BadgeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @extend_schema(summary='Listar minhas badges conquistadas')
    @action(detail=False, methods=['get'], url_path='minhas')
    def minhas_badges(self, request):
        qs = UsuarioBadge.objects.filter(usuario=request.user).select_related('badge').order_by('-data_conquista')
        ser = UsuarioBadgeSerializer(qs, many=True, context={'request': request})
        return Response(ser.data)

    @extend_schema(summary='Listar badges disponíveis para compra')
    @action(detail=False, methods=['get'], url_path='disponiveis')
    def disponiveis(self, request):
        badges_usuario = UsuarioBadge.objects.filter(usuario=request.user).values_list('badge_id', flat=True)
        qs = Badge.objects.filter(ativo=True, tipo='COMPRA').exclude(id__in=badges_usuario)
        ser = BadgeSerializer(qs, many=True, context={'request': request})
        return Response(ser.data)

    @extend_schema(
        summary='Comprar badge',
        request=ComprarBadgeSerializer,
        responses={200: {'type': 'object', 'properties': {
            'sucesso': {'type': 'boolean'},
            'mensagem': {'type': 'string'},
            'saldo_restante': {'type': 'integer'}
        }}}
    )
    @action(detail=False, methods=['post'], url_path='comprar')
    def comprar(self, request):
        ser = ComprarBadgeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        resultado = BadgeService.comprar_badge(request.user, ser.validated_data['badge_id'])
        status_code = resultado.pop('status', status.HTTP_200_OK)
        return Response(resultado, status=status_code)

# ============================================================================
# DASHBOARD
# ============================================================================

@extend_schema(tags=['Dashboard'], summary='Dados do dashboard do usuário')
class DashboardUsuarioView(generics.RetrieveAPIView):
    serializer_class = DashboardUsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context