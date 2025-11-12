from rest_framework import serializers
from .models import Doacao, TipoDoacao, Badge

class DoacaoSerializer(serializers.ModelSerializer):
    
    doador = serializers.StringRelatedField()
    tipo_doacao = serializers.StringRelatedField()

    class Meta:
        model = Doacao
        fields = ['id',
                  'doador',
                  'tipo_doacao',
                  'status',
                  'evidencia_foto',
                  'data_submissao',
        ]
        

class BadgeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Badge
        fields = [
                 'nome', 
                 'descricao', 
                 'imagem_url'
        ]


class CriarDoacaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Doacao
        fields = [
            'tipo_doacao',
            'evidencia_foto'
        ]
    
    def validate_evidencia_foto(self, value):
        if value is None:
            raise serializers.ValidationError("A evidência em foto é obrigatória.")
        return value

