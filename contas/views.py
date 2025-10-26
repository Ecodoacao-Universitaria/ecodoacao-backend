from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from .serializers import CadastroSerializer
from .models import Usuario
import os


# Create your views here.

#cadastro de usuário
class CadastroUsuarioView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = CadastroSerializer
    permission_classes = [AllowAny] #permite que qualquer pessoa possa acessar essa view para se cadastrar



 # view temporária para criar um superusuário na produção

@api_view(['GET'])
@permission_classes([AllowAny])
def criar_superuser_temporario(request):
  
    Usuario = get_user_model()
    
    
    ADMIN_USERNAME = os.getenv('ADMIN_USER', 'admin_render')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin.render@ufrpe.br')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'senha123')

    if not ADMIN_PASSWORD or ADMIN_PASSWORD == 'senha123':
        return Response(
            {"erro": "Senha do admin não configurada nas variáveis de ambiente."}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



    if not Usuario.objects.filter(username=ADMIN_USERNAME).exists():
        try:
            
            Usuario.objects.create_superuser(
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                password=ADMIN_PASSWORD
            )
            return Response(
                {"sucesso": f"Usuário '{ADMIN_USERNAME}' criado com sucesso."}, 
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({"erro": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(
            {"mensagem": f"Usuário '{ADMIN_USERNAME}' já existe."}, 
            status=status.HTTP_200_OK
        )