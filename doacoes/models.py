from django.db import models
from contas.models import Usuario

# Create your models here.

class TipoDoacao(models.Model):

    nome = models.CharField(max_length=100, unique=True)
    moedas_atribuidas = models.IntegerField(default=0)

    def __str__(self):
        return self.nome



class Doacao(models.Model):

    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('APROVADA', 'Aprovada'),
        ('RECUSADA', 'Recusada'),
    ]

    doador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='doacoes')

    tipo_doacao = models.ForeignKey(TipoDoacao, on_delete=models.CASCADE)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE')

    evidencia_foto = models.ImageField(upload_to='evidencias/', blank=True, null=True)

    motivo_recusa = models.TextField(blank=True, null=True)
    data_submissao = models.DateTimeField(auto_now_add=True)


    validado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='doacoes_validadas')
    data_validacao = models.DateTimeField(null=True, blank=True)

    def __str__(self):       
        return f"Doação de {self.tipo_doacao.nome} por {self.doador.username} ({self.status})"