from rest_framework import serializers
from .models import Doacao, TipoDoacao, Badge, UsuarioBadge
from django.contrib.auth import get_user_model

User = get_user_model()

class TipoDoacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDoacao
        fields = ['id', 'nome', 'moedas_atribuidas']
        read_only_fields = ['id']

class DoacaoSerializer(serializers.ModelSerializer):
    doador = serializers.CharField(source='doador.username', read_only=True)
    tipo_doacao = serializers.SerializerMethodField()
    validado_por = serializers.CharField(source='validado_por.username', read_only=True, allow_null=True)
    evidencia_foto = serializers.SerializerMethodField()

    class Meta:
        model = Doacao
        fields = [
            'id', 'doador', 'tipo_doacao', 'descricao', 'evidencia_foto',
            'status', 'data_submissao', 'data_validacao', 'validado_por', 'motivo_recusa'
        ]
        read_only_fields = ['id', 'doador', 'data_submissao', 'data_validacao', 'validado_por', 'status']

    def get_tipo_doacao(self, obj):
        return {
            'id': obj.tipo_doacao.id,
            'nome': obj.tipo_doacao.nome,
            'moedas_atribuidas': obj.tipo_doacao.moedas_atribuidas
        }

    def get_evidencia_foto(self, obj):
        if not obj.evidencia_foto:
            return None
        
        # Se for Cloudinary, já vem com URL completa
        foto_url = str(obj.evidencia_foto)
        
        # Se já for URL absoluta (Cloudinary), retorna direto
        if foto_url.startswith('http'):
            return foto_url
        
        # Se for caminho relativo (desenvolvimento local), constrói URL
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.evidencia_foto.url)
        
        return obj.evidencia_foto.url

class CriarDoacaoSerializer(serializers.ModelSerializer):
    tipo_doacao = serializers.PrimaryKeyRelatedField(queryset=TipoDoacao.objects.all())
    evidencia_foto = serializers.ImageField(required=True)
    descricao = serializers.CharField(required=False, allow_blank=True, max_length=240)

    class Meta:
        model = Doacao
        fields = ['tipo_doacao', 'descricao', 'evidencia_foto']

    def validate_descricao(self, value):
        # Only validate min_length if a non-blank value is provided
        if value and len(value) < 10:
            raise serializers.ValidationError('A descrição deve ter pelo menos 10 caracteres.')
        return value

    def validate_evidencia_foto(self, value):
        # Validate file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if value.size > max_size:
            raise serializers.ValidationError('O tamanho da imagem não pode exceder 5MB.')
        
        # Validate file format
        allowed_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if value.content_type not in allowed_formats:
            raise serializers.ValidationError('Formato de imagem não suportado. Use JPEG, PNG, GIF ou WebP.')
        
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
    icone = serializers.SerializerMethodField()

    class Meta:
        model = Badge
        fields = ['id', 'nome', 'descricao', 'icone', 'tipo', 'custo_moedas', 'ativo']

    def get_icone(self, obj):
        if not obj.icone:
            return None
        
        icone_url = str(obj.icone)
        
        if icone_url.startswith('http'):
            return icone_url
        
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.icone.url)
        
        return obj.icone.url

class UsuarioBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    usuario = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = UsuarioBadge
        fields = ['id', 'usuario', 'badge', 'data_conquista']

class ComprarBadgeSerializer(serializers.Serializer):
    badge_id = serializers.IntegerField(required=True)

class DashboardUsuarioSerializer(serializers.ModelSerializer):
    badges_conquistados = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'saldo_moedas', 'badges_conquistados']

    def get_badges_conquistados(self, obj):
        badges = UsuarioBadge.objects.filter(usuario=obj).select_related('badge')
        return UsuarioBadgeSerializer(badges, many=True, context=self.context).data