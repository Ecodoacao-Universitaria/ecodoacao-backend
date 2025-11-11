from rest_framework import serializers
from .models import Usuario
from doacoes.serializers import BadgeSerializer

class UsuarioSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'saldo_moedas', 'is_staff', 'is_active', 'role', 'date_joined']
    
    def get_role(self, obj):
        return "Admin" if obj.is_staff else "Usuário"


class CadastroSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}


    
    #validação email com final @ufrpe.br
    def validate_email(self, value):
        if not value.endswith('@ufrpe.br'):
            raise serializers.ValidationError("O email deve ser institucional da UFRPE (@ufrpe.br).")
        return value

    # override do método create para criar o usuário com senha hash
    def create(self, validated_data):
        #create_user garante que o usuario não é admin por padrão(is_staff = False) e faz o hash da senha
        usuario = Usuario.objects.create_user(**validated_data)
        return usuario
    

class DashboardUsuarioSerializer(serializers.ModelSerializer):
    badges_conquistados = BadgeSerializer(many=True, read_only=True, source='badges_conquistados.badge') #Acessa o badge relacionado no UsuarioBadge
    role = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'saldo_moedas', 'badges_conquistados', 'role'] #exibir apenas os campos relevantes para o dashboard
    
    def get_role(self, obj):
        return "Admin" if obj.is_staff else "Usuário"