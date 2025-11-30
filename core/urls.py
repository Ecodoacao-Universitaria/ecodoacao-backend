from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.conf import settings 
from rest_framework import serializers, generics
from drf_spectacular.utils import extend_schema, OpenApiTypes

class ApiRootSerializer(serializers.Serializer):
    contas = serializers.CharField()
    doacoes = serializers.CharField()
    docs = serializers.CharField()
    schema = serializers.CharField()

@extend_schema(
    tags=['Root'],
    summary='Índice da API',
    responses=ApiRootSerializer,
)
class ApiRootView(generics.GenericAPIView):
    serializer_class = ApiRootSerializer

    def get(self, request, *args, **kwargs):
        base_url = request.build_absolute_uri('/api/')
        data = {
            "contas": f"{base_url}contas/",
            "doacoes": f"{base_url}doacoes/",
            "docs": request.build_absolute_uri('/api/docs/'),
            "schema": request.build_absolute_uri('/api/schema/'),
        }
        return Response(data)

urlpatterns = [
    # Painel admin
    path('admin/', admin.site.urls),

    # API base
    path('api/', ApiRootView.as_view(), name='api-root'),

    # Apps da API
    path('api/contas/', include('contas.urls')),
    path('api/doacoes/', include('doacoes.urls')),

    # --- Swagger e Schema ---
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc-ui'),
]

# Configuração para servir arquivos de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += path('__debug__/', include('debug_toolbar.urls')),