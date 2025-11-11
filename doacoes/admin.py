from django.contrib import admin
from django.utils.html import format_html
from .models import TipoDoacao, Doacao, Badge, UsuarioBadge


@admin.register(TipoDoacao)
class TipoDoacaoAdmin(admin.ModelAdmin):
    """Administração de Tipos de Doação"""
    list_display = ['nome', 'moedas_atribuidas']
    search_fields = ['nome']
    ordering = ['nome']


@admin.register(Doacao)
class DoacaoAdmin(admin.ModelAdmin):
    """Administração de Doações"""
    list_display = ['id', 'doador', 'tipo_doacao', 'status', 'data_submissao', 'validado_por']
    list_filter = ['status', 'data_submissao', 'tipo_doacao']
    search_fields = ['doador__username', 'doador__email']
    readonly_fields = ['data_submissao', 'data_validacao']
    ordering = ['-data_submissao']
    
    fieldsets = (
        ('Informações da Doação', {
            'fields': ('doador', 'tipo_doacao', 'evidencia_foto', 'data_submissao')
        }),
        ('Validação', {
            'fields': ('status', 'validado_por', 'data_validacao', 'motivo_recusa')
        }),
    )


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    """Administração de Badges"""
    list_display = ['nome', 'custo_moedas', 'imagem_preview']
    search_fields = ['nome', 'descricao']
    ordering = ['nome']
    
    def imagem_preview(self, obj):
        """Exibe preview da imagem do badge"""
        if obj.imagem_url:
            return format_html('<img src="{}" width="50" height="50" />', obj.imagem_url)
        return '-'
    imagem_preview.short_description = 'Preview'


@admin.register(UsuarioBadge)
class UsuarioBadgeAdmin(admin.ModelAdmin):
    """Administração de Badges dos Usuários"""
    list_display = ['usuario', 'badge', 'data_conquista']
    list_filter = ['badge', 'data_conquista']
    search_fields = ['usuario__username', 'badge__nome']
    readonly_fields = ['data_conquista']
    ordering = ['-data_conquista']
