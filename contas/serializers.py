from rest_framework import serializers
from .models import Usuario
from doacoes.serializers import BadgeSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

Usuario = get_user_model()
class EcoTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = getattr(user, 'email', '')
        token['is_staff'] = bool(user.is_staff)
        token['is_superuser'] = bool(user.is_superuser)
        token['role'] = 'ADMIN' if (user.is_staff or user.is_superuser) else 'USUARIO'
        return token
    
    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except Exception:
            from rest_framework.exceptions import AuthenticationFailed
            raise AuthenticationFailed("Credenciais inválidas. Verifique usuário e senha.")

class MeuPerfilSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        model = Usuario
        fields = ("id", "username", "email")
        read_only_fields = ("id",)

    def validate_email(self, value):
        if not value.lower().endswith("@ufrpe.br"):
            raise serializers.ValidationError("O email deve ser institucional da UFRPE (@ufrpe.br).")
        user = self.context["request"].user
        if Usuario.objects.filter(email__iexact=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Email já está em uso.")
        return value

    def validate_username(self, value):
        user = self.context["request"].user
        if Usuario.objects.filter(username__iexact=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Username já está em uso.")
        return value

class AlterarSenhaSerializer(serializers.Serializer):
    senha_atual = serializers.CharField(write_only=True)
    nova_senha = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["senha_atual"]):
            raise serializers.ValidationError({"senha_atual": "Senha atual incorreta."})
        try:
            validate_password(attrs["nova_senha"], user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"nova_senha": e.messages})
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        nova = self.validated_data["nova_senha"]
        user.set_password(nova)
        user.save(update_fields=["password"])
        return user

class UsuarioSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'saldo_moedas', 'is_staff', 'is_active', 'role', 'date_joined']
    
    def get_role(self, obj) -> str:
        return "Admin" if obj.is_staff else "Usuário"

class CadastroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if not value.lower().endswith("@ufrpe.br"):
            raise serializers.ValidationError("O email deve ser institucional da UFRPE (@ufrpe.br).")
        if Usuario.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email já está em uso.")
        return value

    def validate(self, attrs):
            try:
                validate_password(attrs.get("password"), user=None)
            except DjangoValidationError as e:
                raise serializers.ValidationError({"password": e.messages})
            username = attrs.get("username")
            if username and Usuario.objects.filter(username__iexact=username).exists():
                raise serializers.ValidationError({"username": "Username já está em uso."})
            return attrs

    def create(self, validated_data):
        usuario = Usuario.objects.create_user(**validated_data)
        return usuario

class DashboardUsuarioSerializer(serializers.ModelSerializer):
    badges_conquistados = BadgeSerializer(many=True, read_only=True, source='badges_conquistados.badge')
    role = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    is_staff = serializers.BooleanField(read_only=True)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'saldo_moedas', 'badges_conquistados', 'role', 'is_admin', 'is_staff']

    def get_role(self, obj) -> str:
        return 'ADMIN' if (obj.is_staff or obj.is_superuser) else 'USUARIO'

    def get_is_admin(self, obj) -> int:
        return 1 if (obj.is_staff or obj.is_superuser) else 0