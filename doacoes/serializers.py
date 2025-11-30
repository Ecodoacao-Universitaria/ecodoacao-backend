from rest_framework import serializers
from .models import Doacao, Badge, UsuarioBadge, TipoDoacao, Usuario

class TipoDoacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDoacao
        fields = ['id', 'nome', 'moedas_atribuidas']

class DoacaoSerializer(serializers.ModelSerializer):
    doador = serializers.StringRelatedField()
    tipo_doacao = serializers.StringRelatedField()
    validado_por = serializers.StringRelatedField()
    class Meta:
        model = Doacao
        fields = [
            'id','doador','tipo_doacao','status','evidencia_foto',
            'data_submissao','motivo_recusa','descricao',
            'data_validacao','validado_por'
        ]

class ValidarDoacaoSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['APROVADA', 'RECUSADA'])
    motivo_recusa = serializers.CharField(required=False, allow_blank=True)
    def validate(self, attrs):
        if attrs['status'] == 'RECUSADA':
            motivo = attrs.get('motivo_recusa', '').strip()
            if not motivo:
                raise serializers.ValidationError({'motivo_recusa': 'Motivo obrigatório ao recusar.'})
        return attrs

class CriarDoacaoSerializer(serializers.ModelSerializer):
    evidencia_foto = serializers.ImageField(required=True)
    class Meta:
        model = Doacao
        fields = ['id', 'tipo_doacao', 'descricao', 'evidencia_foto']
        extra_kwargs = {
            'tipo_doacao': {'required': True},
            'descricao': {'required': False, 'allow_blank': True},
        }
    def validate_descricao(self, value):
        if value is None:
            return ''
        txt = value.strip()
        if txt and (len(txt) < 10 or len(txt) > 240):
            raise serializers.ValidationError('A descrição deve ter entre 10 e 240 caracteres.')
        return txt
    def validate_evidencia_foto(self, value):
        if not value:
            raise serializers.ValidationError('Envie uma imagem.')
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('Imagem excede 5MB.')
        return value
    def create(self, validated_data):
        validated_data['doador'] = self.context['request'].user
        return super().create(validated_data)

class BadgeSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    class Meta:
        model = Badge
        fields = [
            'id', 'nome', 'descricao', 'icone', 'tipo',
            'tipo_display', 'custo_moedas', 'criterio_doacoes',
            'criterio_moedas', 'ativo'
        ]

class UsuarioBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    class Meta:
        model = UsuarioBadge
        fields = ['id', 'badge', 'data_conquista']

class DashboardUsuarioSerializer(serializers.ModelSerializer):
    badges_conquistados = BadgeSerializer(many=True, read_only=True, source='badges_conquistados.badge') 
    role = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()  
    is_staff = serializers.BooleanField(read_only=True) 

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'saldo_moedas', 'badges_conquistados', 'role', 'is_admin', 'is_staff']

    def get_role(self, obj):
        return "Admin" if obj.is_staff else "Usuário"

    def get_is_admin(self, obj):
        return 1 if obj.is_staff else 0

class ComprarBadgeSerializer(serializers.Serializer):
    badge_id = serializers.IntegerField()