from django.contrib import admin
from django.utils.html import format_html
from .models import TipoDoacao, Doacao, Badge, UsuarioBadge

@admin.register(TipoDoacao)
class TipoDoacaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'moedas_atribuidas']
    search_fields = ['nome']
    ordering = ['nome']


@admin.register(Doacao)
class DoacaoAdmin(admin.ModelAdmin):
    list_display = ['id', 'doador', 'tipo_doacao', 'status', 'data_submissao', 'validado_por']
    list_filter = ['status', 'tipo_doacao', 'data_submissao']
    search_fields = ['doador__username', 'doador__email']
    readonly_fields = ['data_submissao', 'data_validacao']
    ordering = ['-data_submissao']
    
    fieldsets = (
        ('Informações da Doação', {
            'fields': ('doador', 'tipo_doacao', 'descricao', 'evidencia_foto', 'status')
        }),
        ('Validação', {
            'fields': ('validado_por', 'data_validacao', 'motivo_recusa')
        }),
        ('Datas', {
            'fields': ('data_submissao',)
        }),
    )


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'icone_preview', 'custo_moedas', 'criterio_doacoes', 'ativo']
    list_filter = ['tipo', 'ativo']
    search_fields = ['nome', 'descricao']
    ordering = ['tipo', 'custo_moedas']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'icone', 'tipo', 'ativo')
        }),
        ('Critérios de Conquista', {
            'fields': ('criterio_doacoes', 'criterio_moedas'),
            'description': 'Deixe em branco para badges de compra'
        }),
        ('Compra', {
            'fields': ('custo_moedas',),
            'description': 'Defina 0 para badges de conquista automática'
        }),
    )
    
    def icone_preview(self, obj):
        """Exibe preview do ícone da badge"""
        if obj.icone:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.icone.url
            )
        return "Sem ícone"
    icone_preview.short_description = 'Preview'


@admin.register(UsuarioBadge)
class UsuarioBadgeAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'badge', 'data_conquista']
    list_filter = ['badge', 'data_conquista']
    search_fields = ['usuario__username', 'badge__nome']
    readonly_fields = ['data_conquista']
    ordering = ['-data_conquista']
    
    fieldsets = (
        ('Badge Conquistada', {
            'fields': ('usuario', 'badge', 'data_conquista')
        }),
    )