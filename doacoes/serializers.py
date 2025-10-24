from rest_framework import serializers
from .models import Doacao, TipoDoacao

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
        