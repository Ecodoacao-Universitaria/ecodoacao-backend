from django.db.models import Sum
from django.db import transaction
from .models import Badge, UsuarioBadge, Doacao
from rest_framework import status

class BadgeService:
    @staticmethod
    def verificar_e_atribuir_badges(usuario):
        badges_conquistadas = []
        total_doacoes_aprovadas = Doacao.objects.filter(doador=usuario, status='APROVADA').count()
        total_moedas_ganhas = Doacao.objects.filter(doador=usuario, status='APROVADA').aggregate(
            total=Sum('tipo_doacao__moedas_atribuidas')
        )['total'] or 0
        badges_disponiveis = Badge.objects.filter(tipo='CONQUISTA', ativo=True).exclude(
            usuariobadge__usuario=usuario
        )
        for badge in badges_disponiveis:
            conquistou = False
            if badge.criterio_doacoes and total_doacoes_aprovadas >= badge.criterio_doacoes:
                conquistou = True
            if badge.criterio_moedas and total_moedas_ganhas >= badge.criterio_moedas:
                conquistou = True
            if conquistou:
                UsuarioBadge.objects.create(usuario=usuario, badge=badge)
                badges_conquistadas.append(badge)
        return badges_conquistadas

    @staticmethod
    def comprar_badge(usuario, badge_id):
        try:
            badge = Badge.objects.get(id=badge_id, tipo='COMPRA', ativo=True)
        except Badge.DoesNotExist:
            return {'sucesso': False, 'codigo': 'BADGE_INEXISTENTE', 'mensagem': 'Badge não disponível para compra', 'status': status.HTTP_400_BAD_REQUEST}
        if UsuarioBadge.objects.filter(usuario=usuario, badge=badge).exists():
            return {'sucesso': False, 'codigo': 'JA_POSSUI_BADGE', 'mensagem': 'Você já possui esta badge', 'status': status.HTTP_400_BAD_REQUEST}
        if usuario.saldo_moedas < badge.custo_moedas:
            return {'sucesso': False, 'codigo': 'SALDO_INSUFICIENTE', 'mensagem': f'Saldo insuficiente. Necessário: {badge.custo_moedas} moedas', 'status': 402}
        usuario.saldo_moedas -= badge.custo_moedas
        usuario.save(update_fields=['saldo_moedas'])
        UsuarioBadge.objects.create(usuario=usuario, badge=badge)
        return {'sucesso': True, 'codigo': 'COMPRA_OK', 'mensagem': f'Badge "{badge.nome}" adquirida com sucesso!', 'saldo_restante': usuario.saldo_moedas, 'status': status.HTTP_200_OK}

    @staticmethod
    def listar_badges_usuario(usuario):
        return UsuarioBadge.objects.filter(usuario=usuario).select_related('badge')

    @staticmethod
    def listar_badges_disponiveis(usuario):
        return Badge.objects.filter(tipo='COMPRA', ativo=True).exclude(usuariobadge__usuario=usuario)

    @staticmethod
    def premiar_doacao_aprovada(doacao: Doacao):
        usuario = doacao.doador
        tipo = doacao.tipo_doacao
        with transaction.atomic():
            if tipo and tipo.moedas_atribuidas:
                usuario.saldo_moedas = (usuario.saldo_moedas or 0) + tipo.moedas_atribuidas
                usuario.save(update_fields=['saldo_moedas'])
            total_aprovadas = Doacao.objects.filter(doador=usuario, status='APROVADA').count()
            conquistas = Badge.objects.filter(ativo=True, tipo='CONQUISTA')
            novas = []
            for b in conquistas:
                ok_doacoes = b.criterio_doacoes and total_aprovadas >= b.criterio_doacoes
                ok_moedas = b.criterio_moedas and usuario.saldo_moedas >= b.criterio_moedas
                if (ok_doacoes or ok_moedas) and not UsuarioBadge.objects.filter(usuario=usuario, badge=b).exists():
                    UsuarioBadge.objects.create(usuario=usuario, badge=b)
                    novas.append(b)
        return usuario, novas