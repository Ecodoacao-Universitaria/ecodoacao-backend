from datetime import timezone
from django.db import models
from contas.models import Usuario
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField

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

    evidencia_foto = CloudinaryField(
        'evidencia',
        folder='evidencias',
        transformation={
            'quality': 'auto:eco',
            'fetch_format': 'auto',
        }
    )

    motivo_recusa = models.TextField(blank=True, null=True)
    data_submissao = models.DateTimeField(auto_now_add=True)
    descricao = models.TextField(blank=True, null=True, max_length=500)

    validado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='doacoes_validadas')
    data_validacao = models.DateTimeField(null=True, blank=True)

    def aprovar(self, usuario_validador):
        self.status = 'APROVADA'
        self.motivo_recusa = None
        self.data_validacao = timezone.now()
        self.validado_por = usuario_validador
        self.save()

    def recusar(self, usuario_validador, motivo):
        self.status = 'RECUSADA'
        self.motivo_recusa = motivo
        self.data_validacao = timezone.now()
        self.validado_por = usuario_validador
        self.save()

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
    TIPO_CHOICES = [
        ('CONQUISTA', 'Conquista Automática'),
        ('COMPRA', 'Disponível para Compra'),
        ('ESPECIAL', 'Badge Especial'),
    ]
    
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    icone = models.ImageField(upload_to='badges/', blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='CONQUISTA')
    custo_moedas = models.IntegerField(default=0, help_text="0 para badges de conquista")
    criterio_doacoes = models.IntegerField(null=True, blank=True, help_text="Número de doações necessárias")
    criterio_moedas = models.IntegerField(null=True, blank=True, help_text="Total de moedas ganhas necessárias")
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'badges'
        verbose_name = 'Badge'
        verbose_name_plural = 'Badges'
        ordering = ['tipo', 'custo_moedas']

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"
    

class UsuarioBadge(models.Model):

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='badges_conquistados')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    data_conquista = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Garantir que um usuário não possa conquistar o mesmo badge mais de uma vez
        unique_together = ('usuario', 'badge')

    def __str__(self):
        return f"{self.usuario.username} - {self.badge.nome}"
