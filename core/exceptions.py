from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def drf_exception_handler(exc, context):
    """
    Padroniza erros em:
    { "erro": "mensagem", "codigo": "string", "detalhes": {...} }
    """
    resp = exception_handler(exc, context)
    if resp is None:
        # erro não tratado pelo DRF
        return Response({
            "erro": str(exc),
            "codigo": exc.__class__.__name__,
            "detalhes": {}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    data = resp.data
    # Ajusta formatos comuns do DRF/serializers
    if isinstance(data, dict):
        msg = data.get('detail') or next(iter(data.values()), None)
        detalhes = data if 'detail' not in data else {}
    else:
        msg = str(data)
        detalhes = {}

    return Response({
        "erro": msg if isinstance(msg, str) else "Erro na requisição",
        "codigo": exc.__class__.__name__,
        "detalhes": data if isinstance(data, dict) else {}
    }, status=resp.status_code)