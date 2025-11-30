from rest_framework import serializers
from .models import Doacao, TipoDoacao, Badge, UsuarioBadge
from django.contrib.auth import get_user_model
from typing import Optional

Usuario = get_user_model()

class TipoDoacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDoacao
        fields = ['id', 'nome', 'moedas', 'descricao']

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
        read_only_fields = ['id', 'doador', 'data_submissao', 'data_validacao', 'validado_por']

    def get_doador(self, obj: Doacao) -> str:
        return obj.doador.username if obj.doador else "Anônimo"

    def get_tipo_doacao(self, obj: Doacao) -> str:
        return obj.tipo_doacao.nome if obj.tipo_doacao else "Tipo não especificado"

    def get_evidencia_foto(self, obj: Doacao) -> Optional[str]:
        """Retorna a URL completa da imagem com transformações do Cloudinary"""
        if not obj.evidencia_foto:
            return None
        
        try:
            # Se já for uma URL completa, retorna
            if obj.evidencia_foto.url.startswith('http'):
                return obj.evidencia_foto.url
            
            # Constrói a URL com transformações
            url = str(obj.evidencia_foto.url)
            
            # Se a URL não contém transformações, adiciona
            if '/upload/' in url and '/c_limit,h_800,w_800/' not in url:
                url = url.replace('/upload/', '/upload/c_limit,h_800,w_800/')
            
            return url
        except Exception:
            return None

class CriarDoacaoSerializer(serializers.ModelSerializer):
    """Serializer específico para criação de doações"""
    class Meta:
        model = Doacao
        fields = ['tipo_doacao', 'descricao', 'evidencia_foto']

    def validate_evidencia_foto(self, value):
        """Valida o arquivo de imagem"""
        if not value:
            raise serializers.ValidationError("A foto da doação é obrigatória.")
        
        # Valida tipo de arquivo
        valid_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if hasattr(value, 'content_type') and value.content_type not in valid_types:
            raise serializers.ValidationError(
                "Formato inválido. Use: JPEG, PNG, GIF ou WebP."
            )
        
        # Valida tamanho (10MB)
        if hasattr(value, 'size') and value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("A imagem deve ter no máximo 10MB.")
        
        return value

    def validate_descricao(self, value):
        """Valida a descrição"""
        if value and len(value) > 240:
            raise serializers.ValidationError("A descrição deve ter no máximo 240 caracteres.")
        if value and len(value) < 10:
            raise serializers.ValidationError("A descrição deve ter no mínimo 10 caracteres.")
        return value

class BadgeSerializer(serializers.ModelSerializer):
    icone = serializers.SerializerMethodField()
    
    class Meta:
        model = Badge
        fields = [
            'id', 
            'nome', 
            'descricao', 
            'icone',
            'tipo',
            'custo_moedas',
            'criterio_doacoes',
            'criterio_moedas',
            'ativo'
        ]
        read_only_fields = ['id']

    def get_icone(self, obj: Badge) -> Optional[str]:
        """Retorna a URL completa do ícone com transformações do Cloudinary"""
        if not obj.icone:
            return None
        
        try:
            # Se já for uma URL completa, retorna
            if obj.icone.url.startswith('http'):
                return obj.icone.url
            
            # Constrói a URL com transformações
            url = str(obj.icone.url)
            
            # Adiciona transformações se não existirem
            if '/upload/' in url and '/c_limit,h_200,w_200/' not in url:
                url = url.replace('/upload/', '/upload/c_limit,h_200,w_200/')
            
            return url
        except Exception:
            return None

class UsuarioBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    
    class Meta:
        model = UsuarioBadge
        fields = ['id', 'badge', 'data_conquista']
        read_only_fields = ['id', 'data_conquista']

class BadgeDisponiveisSerializer(serializers.ModelSerializer):
    """Serializer para badges disponíveis para compra"""
    icone = serializers.SerializerMethodField()
    
    class Meta:
        model = Badge
        fields = ['id', 'nome', 'descricao', 'icone', 'custo_moedas']

    def get_icone(self, obj: Badge) -> Optional[str]:
        """Retorna a URL completa do ícone com transformações do Cloudinary"""
        if not obj.icone:
            return None
        
        try:
            if obj.icone.url.startswith('http'):
                return obj.icone.url
            
            url = str(obj.icone.url)
            
            if '/upload/' in url and '/c_limit,h_200,w_200/' not in url:
                url = url.replace('/upload/', '/upload/c_limit,h_200,w_200/')
            
            return url
        except Exception:
            return None