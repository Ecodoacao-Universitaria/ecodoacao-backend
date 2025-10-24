from django.urls import path
from .views import AdminDoacoesPendentesView

urlpatterns = [
    path('admin/pendentes/', AdminDoacoesPendentesView.as_view(),
            name='admin_doacoes_pendentes'),
]