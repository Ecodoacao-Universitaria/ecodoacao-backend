from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# View opcional — só um índice simples
class ApiRootView(APIView):
    def get(self, request, *args, **kwargs):
        base_url = request.build_absolute_uri('/api/')
        return Response({
            "contas": f"{base_url}contas/",
            "doacoes": f"{base_url}doacoes/",
            "docs": request.build_absolute_uri('/api/docs/'),
            "schema": request.build_absolute_uri('/api/schema/'),
        })


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