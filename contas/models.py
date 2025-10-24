from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    #abstractuser já tem username, email, password, first_name, last_name
    #is_staff (true se o usuário pode acessar o admin), is_active (True para usuários ativos)

    saldo_moedas= models.IntegerField(default=0, verbose_name="Saldo de Moedas")


    def __str__(self):
        role = "Admin" if self.is_staff else "Usuário"
        return f"{self.username} ({role})"
