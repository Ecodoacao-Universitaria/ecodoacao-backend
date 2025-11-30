from rest_framework import generics, status, viewsets, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.utils import timezone
from .models import Doacao, Badge, UsuarioBadge
from .serializers import (
    DoacaoSerializer, 
    CriarDoacaoSerializer, 
    ValidarDoacaoSerializer,
    BadgeSerializer,
    UsuarioBadgeSerializer,
    ComprarBadgeSerializer,
    DashboardUsuarioSerializer
)
from .services import BadgeService


@extend_schema(
    tags=['Doações'],
    summary='Submeter nova doação',
)
class CriarDoacaoView(generics.CreateAPIView):
    serializer_class = CriarDoacaoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(doador=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Retornar resposta completa
        doacao = serializer.instance
        output_serializer = DoacaoSerializer(doacao)
        headers = self.get_success_headers(output_serializer.data)
        return Response(
            output_serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )

@extend_schema(
    tags=['Doações'],
    summary='Histórico de doações do usuário',
    parameters=[
        OpenApiParameter(
            name='status',
            description='Filtrar por status (PENDENTE, APROVADA, RECUSADA)',
            required=False,
            type=str
        ),
    ]
)
class HistoricoDoacoesView(generics.ListAPIView):
    serializer_class = DoacaoSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        queryset = Doacao.objects.filter(doador=self.request.user).select_related(
            'tipo_doacao', 'validado_por'
        ).order_by('-data_submissao')
        status_filtro = self.request.query_params.get('status')
        if status_filtro:
            queryset = queryset.filter(status=status_filtro.upper())
        return queryset

@extend_schema(
    tags=['Admin - Doações'],
    summary='Listar doações pendentes',
)
class AdminDoacoesPendentesView(generics.ListAPIView):
    serializer_class = DoacaoSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return Doacao.objects.filter(
            status='PENDENTE'
        ).select_related(
            'doador', 'tipo_doacao'
        ).order_by('-data_submissao')

@extend_schema(
    tags=['Admin - Doações'],
    summary='Validar doação (aprovar/recusar)',
)
class AdminAtualizarDoacaoView(generics.UpdateAPIView):
    queryset = Doacao.objects.all()
    serializer_class = ValidarDoacaoSerializer
    permission_classes = [IsAdminUser]
    def update(self, request, *args, **kwargs):
        doacao = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if doacao.status != 'PENDENTE':
            return Response({'erro':'Apenas doações pendentes podem ser validadas.'}, status=status.HTTP_400_BAD_REQUEST)
        novo_status = serializer.validated_data['status']
        doacao.status = novo_status
        doacao.validado_por = request.user
        doacao.data_validacao = timezone.now()
        if novo_status == 'RECUSADA':
            doacao.motivo_recusa = serializer.validated_data.get('motivo_recusa','')
        doacao.save()
        if novo_status == 'APROVADA':
            usuario, novas = BadgeService.premiar_doacao_aprovada(doacao)
            return Response({
                'sucesso': True,
                'mensagem': f'Doação aprovada! +{doacao.tipo_doacao.moedas_atribuidas} moedas.',
                'saldo_restante': usuario.saldo_moedas,
                'badges_conquistadas': [b.nome for b in novas],
            }, status=status.HTTP_200_OK)
        return Response({
            'sucesso': True,
            'mensagem': 'Doação recusada.',
            'motivo_recusa': doacao.motivo_recusa
        }, status=status.HTTP_200_OK)

@extend_schema(tags=['Admin - Badges'], summary='Criar badge (admin)')
class AdminBadgeViewSet(viewsets.ModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'post', 'patch', 'delete']  

@extend_schema(tags=['Badges'])
class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Badge.objects.filter(ativo=True)
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='minhas-badges')
    def minhas_badges(self, request):
        qs = BadgeService.listar_badges_usuario(request.user)
        ser = UsuarioBadgeSerializer(qs, many=True)
        return Response(ser.data)

    @action(detail=False, methods=['get'], url_path='disponiveis')
    def disponiveis(self, request):
        qs = BadgeService.listar_badges_disponiveis(request.user)
        ser = BadgeSerializer(qs, many=True)
        return Response(ser.data)

    @action(detail=False, methods=['post'], url_path='comprar')
    def comprar(self, request):
        ser = ComprarBadgeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        resultado = BadgeService.comprar_badge(request.user, ser.validated_data['badge_id'])
        status_code = resultado.get('status', (status.HTTP_200_OK if resultado.get('sucesso') else status.HTTP_400_BAD_REQUEST))
        return Response(resultado, status=status_code)
        
class DashboardUsuarioView(generics.RetrieveAPIView):
    serializer_class = DashboardUsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user