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
  
    try:
        Usuario = get_user_model()
        
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

        
        if not Usuario.objects.filter(username=ADMIN_USERNAME).exists():
            
            # Tenta criar o superusuário
            Usuario.objects.create_superuser(
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