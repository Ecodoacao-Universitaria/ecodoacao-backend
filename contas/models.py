from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    #abstractuser já tem username, email, password, first_name, last_name
    #is_staff (true se o usuário pode acessar o admin), is_active (True para usuários ativos)

    saldo_moedas = models.IntegerField(default=0, verbose_name="Saldo de Moedas")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        ordering = ['-date_joined']
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['is_staff']),
        ]

    def __str__(self):
        role = "Admin" if self.is_staff else "Usuário"
        status = "Ativo" if self.is_active else "Inativo"
        return f"{self.username} ({role} - {status})"
