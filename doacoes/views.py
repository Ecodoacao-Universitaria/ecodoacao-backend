from rest_framework import generics
from rest_framework.permissions import IsAdminUser # Importante!
from .models import Doacao
from .serializers import DoacaoSerializer

# Create your views here.

class AdminDoacoesPendentesView(generics.ListAPIView):
  
    queryset = Doacao.objects.filter(status='PENDENTE')
    serializer_class = DoacaoSerializer
    permission_classes = [IsAdminUser]  # Apenas administradores podem acessar esta view(is_staff=True)

    def get_queryset(self):
        return Doacao.objects.filter(status='PENDENTE').order_by('data_submissao')