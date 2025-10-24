
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import CadastroSerializer
from .models import Usuario

# Create your views here.

#cadastro de usuário
class CadastroUsuarioView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = CadastroSerializer
    permission_classes = [AllowAny] #permite que qualquer pessoa possa acessar essa view para se cadastrar


