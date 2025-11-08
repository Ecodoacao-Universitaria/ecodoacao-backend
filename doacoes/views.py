from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from .models import Doacao
from .serializers import DoacaoSerializer, CriarDoacaoSerializer
from django.utils import timezone

# Create your views here.

class AdminDoacoesPendentesView(generics.ListAPIView):
  
    queryset = Doacao.objects.filter(status='PENDENTE')
    serializer_class = DoacaoSerializer
    permission_classes = [IsAdminUser]  # Apenas administradores podem acessar esta view(is_staff=True)

    def get_queryset(self):
        return Doacao.objects.filter(status='PENDENTE').order_by('data_submissao')
    

class CriarDoacaoView(generics.CreateAPIView):
    queryset = Doacao.objects.all()
    serializer_class = CriarDoacaoSerializer
    permission_classes = [IsAuthenticated] # Só usuários logados podem doar

    def perform_create(self, serializer):
        # Associa automaticamente o usuário logado como o 'doador'
        serializer.save(doador=self.request.user)


class AdminAtualizarDoacaoView(generics.RetrieveUpdateAPIView):
    queryset = Doacao.objects.all()
    serializer_class = DoacaoSerializer
    permission_classes = [IsAdminUser]  # Apenas administradores podem acessar esta view(is_staff=True)

    http_method_names = ['put', 'patch']  # Permitir apenas métodos put e patch

    def update(self, request, *args, **kwargs):

        doacao = self.get_object() # pega o objeto da doação a ser atualizada ex /api/doacoes/admin/validar/3/


        novo_status = request.data.get('status') # obtém o novo status do corpo do request

        if doacao.status != 'PENDENTE':
            return Response(
                {"erro": "Esta doação já foi validada."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if novo_status == 'APROVADO':
            doador = doacao.doador
            moedas_ganhas = doacao.tipo_doacao.moedas_atribuidas
            
            # Atualiza o saldo do usuário
            doador.saldo_moedas += moedas_ganhas
            doador.save()
            
            # Atualiza a doação
            doacao.status = 'APROVADO'

        elif novo_status == 'REJEITADO':
            motivo = request.data.get('motivo_rejeicao')

            if not motivo:
                return Response(
                    {"erro": "Motivo de rejeição é obrigatório."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            doacao.status = 'REJEITADO'
            doacao.motivo_rejeicao = motivo

        else:
            return Response(
                {"erro": "Status inválido. Use 'APROVADO' ou 'REJEITADO'."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Salva as mudanças na doação
        doacao.validado_por = request.user
        doacao.data_validacao = timezone.now()
        doacao.save()
        
        return Response(DonationSerializer(doacao).data, status=status.HTTP_200_OK)
    

class HistoricoDoacoesView(generics.ListAPIView):

    serializer_class = DoacaoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filtra o queryset para retornar apenas doações do usuário que está fazendo o request.
        return Doacao.objects.filter(doador=self.request.user).order_by('-data_submissao')