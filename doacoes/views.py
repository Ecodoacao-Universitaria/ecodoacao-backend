from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.utils import timezone

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
from .services import processar_validacao_doacao, processar_compra_badge

class CustomPagination(generics.pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

@extend_schema(tags=['Doações'], summary='Listar tipos de doação')
class ListarTiposDoacaoView(generics.ListAPIView):
    queryset = TipoDoacao.objects.filter(ativo=True)
    serializer_class = TipoDoacaoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

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

        resultado = processar_validacao_doacao(
            doacao=doacao,
            novo_status=serializer.validated_data['status'],
            validado_por=request.user,
            motivo_recusa=serializer.validated_data.get('motivo_recusa')
        )

        return Response(resultado, status=status.HTTP_200_OK)

@extend_schema(tags=['Badges'], summary='Listar badges disponíveis')
class ListarBadgesDisponiveisView(generics.ListAPIView):
    serializer_class = BadgeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        usuario = self.request.user
        badges_usuario = UsuarioBadge.objects.filter(usuario=usuario).values_list('badge_id', flat=True)
        return Badge.objects.filter(ativo=True, tipo='COMPRA').exclude(id__in=badges_usuario)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

@extend_schema(tags=['Badges'], summary='Listar minhas badges')
class ListarMinhasBadgesView(generics.ListAPIView):
    serializer_class = UsuarioBadgeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        return UsuarioBadge.objects.filter(usuario=self.request.user).select_related('badge').order_by('-data_conquista')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

@extend_schema(tags=['Badges'], summary='Comprar badge')
@api_view(['POST'])
def comprar_badge(request):
    serializer = ComprarBadgeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    badge_id = serializer.validated_data['badge_id']
    resultado = processar_compra_badge(usuario=request.user, badge_id=badge_id)
    
    return Response(resultado, status=status.HTTP_200_OK if resultado['sucesso'] else status.HTTP_400_BAD_REQUEST)