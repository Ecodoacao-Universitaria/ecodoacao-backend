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

    class Meta:
        ordering = ['-data_submissao']
        verbose_name = "Doação"
        verbose_name_plural = "Doações"
        indexes = [
            models.Index(fields=['status', 'data_submissao']),
            models.Index(fields=['doador', 'status']),
        ]

    def __str__(self):       
        return f"Doação de {self.tipo_doacao.nome} por {self.doador.username} ({self.status})"


class Badge(models.Model):
    
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(help_text="Critério de conquista")
    custo_moedas = models.IntegerField(default=0, help_text="Custo para 'comprar' com moedas")
    # URL da imagem do badge no S3
    imagem_url = models.URLField(max_length=500, blank=True)

    def __str__(self):
        return self.nome
    

class UsuarioBadge(models.Model):

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='badges_conquistados')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    data_conquista = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Garantir que um usuário não possa conquistar o mesmo badge mais de uma vez
        unique_together = ('usuario', 'badge')

    def __str__(self):
        return f"{self.usuario.username} - {self.badge.nome}"
