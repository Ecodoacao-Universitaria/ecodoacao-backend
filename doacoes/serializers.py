from rest_framework import serializers
from .models import Doacao, TipoDoacao, Badge, UsuarioBadge
from django.contrib.auth import get_user_model
from typing import Optional

Usuario = get_user_model()

class TipoDoacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDoacao
        fields = ['id', 'nome', 'moedas_atribuidas']
        read_only_fields = ['id']

class DoacaoSerializer(serializers.ModelSerializer):
    doador = serializers.SerializerMethodField()
    tipo_doacao = serializers.SerializerMethodField()
    validado_por = serializers.CharField(source='validado_por.username', read_only=True, allow_null=True)
    evidencia_foto = serializers.SerializerMethodField()

    class Meta:
        model = Doacao
        fields = [
            'id', 
            'doador', 
            'tipo_doacao', 
            'descricao',
            'data_submissao', 
            'data_validacao',
            'validado_por',
            'status', 
            'motivo_recusa', 
            'evidencia_foto'
        ]
        read_only_fields = ['id', 'doador', 'data_submissao', 'data_validacao', 'validado_por', 'status']

    def get_doador(self, obj: Doacao) -> str:
        return obj.doador.username if obj.doador else "Anônimo"

    def get_tipo_doacao(self, obj: Doacao) -> dict:
        return {
            'id': obj.tipo_doacao.id,
            'nome': obj.tipo_doacao.nome,
            'moedas_atribuidas': obj.tipo_doacao.moedas_atribuidas
        }

    def get_evidencia_foto(self, obj: Doacao) -> Optional[str]:
        """Retorna a URL completa da imagem do Cloudinary"""
        if not obj.evidencia_foto:
            return None
        
        try:
            # Cloudinary já aplica as transformações definidas no modelo
            return obj.evidencia_foto.url
        except (AttributeError, ValueError):
            return None

class CriarDoacaoSerializer(serializers.ModelSerializer):
    """Serializer específico para criação de doações"""
    tipo_doacao = serializers.PrimaryKeyRelatedField(queryset=TipoDoacao.objects.all())
    evidencia_foto = serializers.ImageField(required=True)
    descricao = serializers.CharField(required=False, allow_blank=True, max_length=240)

    class Meta:
        model = Doacao
        fields = ['tipo_doacao', 'descricao', 'evidencia_foto']

    def validate_descricao(self, value):
        """Valida a descrição"""
        if value and len(value) < 10:
            raise serializers.ValidationError("A descrição deve ter no mínimo 10 caracteres.")
        return value

    def validate_evidencia_foto(self, value):
        """Valida o arquivo de imagem"""
        try:
            # Valida tipo de arquivo
            valid_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if value.content_type not in valid_types:
                raise serializers.ValidationError(
                    "Formato inválido. Use: JPEG, PNG, GIF ou WebP."
                )
            
            # Valida tamanho (10MB)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("A imagem deve ter no máximo 10MB.")
        except AttributeError:
            raise serializers.ValidationError("Arquivo de imagem inválido.")
        
        return value

    def create(self, validated_data):
        validated_data['doador'] = self.context['request'].user
        return super().create(validated_data)

class ValidarDoacaoSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['APROVADA', 'RECUSADA'], required=True)
    motivo_recusa = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate(self, data):
        if data['status'] == 'RECUSADA' and not data.get('motivo_recusa'):
            raise serializers.ValidationError({
                'motivo_recusa': 'O motivo da recusa é obrigatório quando o status é RECUSADA.'
            })
        return data

class BadgeSerializer(serializers.ModelSerializer):
    icone_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Badge
        fields = [
            'id', 
            'nome', 
            'descricao', 
            'icone_url',
            'tipo',
            'custo_moedas',
            'criterio_doacoes',
            'criterio_moedas',
            'ativo'
        ]
        read_only_fields = ['id']

    def get_icone_url(self, obj: Badge) -> Optional[str]:
        """Retorna a URL completa do ícone do Cloudinary"""
        if not obj.icone:
            return None
        
        try:
            return obj.icone.url
        except (AttributeError, ValueError):
            return None

class UsuarioBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    usuario = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = UsuarioBadge
        fields = ['id', 'usuario', 'badge', 'data_conquista']
        read_only_fields = ['id', 'data_conquista']

class ComprarBadgeSerializer(serializers.Serializer):
    badge_id = serializers.IntegerField(required=True)

class DashboardUsuarioSerializer(serializers.ModelSerializer):
    badges_conquistados = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'saldo_moedas', 'badges_conquistados']

    def get_badges_conquistados(self, obj: Usuario) -> list:
        badges = UsuarioBadge.objects.filter(usuario=obj).select_related('badge')
        return UsuarioBadgeSerializer(badges, many=True, context=self.context).data
