from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """
    Classe personalizada para gerenciamento de usuários no admin do Django
    """
    
    # Campos exibidos na lista de usuários
    list_display = ['username', 'email', 'get_role', 'get_status', 'saldo_moedas', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'date_joined', 'is_superuser']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    # Ordenação padrão
    ordering = ['-date_joined']
    
    # Configuração dos fieldsets (seções do formulário de edição)
    fieldsets = (
        (None, {
            'fields': ('username', 'password', 'email')
        }),
        (_('Informações Pessoais'), {
            'fields': ('first_name', 'last_name')
        }),
        (_('Dados do Ecodoação'), {
            'fields': ('saldo_moedas',),
            'classes': ('collapse',)
        }),
        (_('Permissões'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        (_('Datas Importantes'), {
            'fields': ('last_login', 'date_joined', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    # Campos somente leitura
    readonly_fields = ('date_joined', 'last_login', 'criado_em', 'atualizado_em')
    
    # Fieldsets para criação de novo usuário
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        (_('Permissões'), {
            'classes': ('wide',),
            'fields': ('is_staff', 'is_superuser'),
        }),
    )
    
    # Ações personalizadas
    actions = ['make_admin', 'remove_admin', 'activate_users', 'deactivate_users']
    
    def get_role(self, obj):
        """Exibe o role (Admin ou Usuário)"""
        if obj.is_superuser:
            return "Superusuário"
        elif obj.is_staff:
            return "Admin"
        else:
            return "Usuário"
    get_role.short_description = "Função"
    
    def get_status(self, obj):
        """Exibe o status (Ativo ou Inativo)"""
        return "✓ Ativo" if obj.is_active else "✗ Inativo"
    get_status.short_description = "Status"
    
    @admin.action(description="Promover selecionados para Admin")
    def make_admin(self, request, queryset):
        """Ação para promover usuários a admin"""
        updated = queryset.update(is_staff=True)
        self.message_user(request, f"{updated} usuário(s) promovido(s) a admin.")
    
    @admin.action(description="Rebaixar selecionados para Usuário")
    def remove_admin(self, request, queryset):
        """Ação para rebaixar admins a usuários normais"""
        # Proteção: não permitir remover superusuários
        if queryset.filter(is_superuser=True).exists():
            self.message_user(
                request,
                "Não é possível rebaixar superusuários.",
                level='ERROR'
            )
            return
        
        updated = queryset.exclude(is_superuser=True).update(is_staff=False)
        self.message_user(request, f"{updated} admin(ns) rebaixado(s) para usuário.")
    
    @admin.action(description="Ativar selecionados")
    def activate_users(self, request, queryset):
        """Ação para ativar usuários"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} usuário(s) ativado(s).")
    
    @admin.action(description="Desativar selecionados")
    def deactivate_users(self, request, queryset):
        """Ação para desativar usuários"""
        # Proteção: não permitir desativar superusuários
        if queryset.filter(is_superuser=True).exists():
            self.message_user(
                request,
                "Não é possível desativar superusuários.",
                level='ERROR'
            )
            return
        
        updated = queryset.exclude(is_superuser=True).update(is_active=False)
        self.message_user(request, f"{updated} usuário(s) desativado(s).")
