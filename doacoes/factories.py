import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory
from django.utils import timezone
from .models import TipoDoacao, Doacao, Badge, UsuarioBadge
from contas.factories import UsuarioFactory, AdminFactory


class TipoDoacaoFactory(DjangoModelFactory):
    """Factory para criar tipos de doação"""
    
    class Meta:
        model = TipoDoacao
        django_get_or_create = ('nome',)
    
    nome = factory.Sequence(lambda n: f'Tipo {n}')
    moedas_atribuidas = factory.Faker('random_int', min=10, max=100)


class DoacaoPendenteFactory(DjangoModelFactory):
    """Factory para criar doação pendente"""
    
    class Meta:
        model = Doacao
    
    doador = SubFactory(UsuarioFactory)
    tipo_doacao = SubFactory(TipoDoacaoFactory)
    status = 'PENDENTE'
    evidencia_foto = factory.django.ImageField(color='blue', width=100, height=100)


class DoacaoAprovadaFactory(DjangoModelFactory):
    """Factory para criar doação aprovada"""
    
    class Meta:
        model = Doacao
    
    doador = SubFactory(UsuarioFactory)
    tipo_doacao = SubFactory(TipoDoacaoFactory)
    status = 'APROVADA'
    evidencia_foto = factory.django.ImageField(color='green', width=100, height=100)
    validado_por = SubFactory(AdminFactory)
    data_validacao = factory.LazyFunction(timezone.now)  # ✅ CORRIGIDO


class DoacaoRecusadaFactory(DjangoModelFactory):
    """Factory para criar doação recusada"""
    
    class Meta:
        model = Doacao
    
    doador = SubFactory(UsuarioFactory)
    tipo_doacao = SubFactory(TipoDoacaoFactory)
    status = 'RECUSADA'
    evidencia_foto = factory.django.ImageField(color='red', width=100, height=100)
    validado_por = SubFactory(AdminFactory)
    motivo_recusa = factory.Faker('sentence')
    data_validacao = factory.LazyFunction(timezone.now)  # ✅ CORRIGIDO


class BadgeConquistaFactory(DjangoModelFactory):
    """Factory para badge de conquista"""
    
    class Meta:
        model = Badge
        django_get_or_create = ('nome',)
    
    nome = factory.Sequence(lambda n: f'Badge Conquista {n}')
    descricao = factory.Faker('sentence')
    tipo = 'CONQUISTA'
    criterio_doacoes = factory.Faker('random_int', min=1, max=10)
    custo_moedas = 0
    ativo = True


class BadgeCompraFactory(DjangoModelFactory):
    """Factory para badge de compra"""
    
    class Meta:
        model = Badge
        django_get_or_create = ('nome',)
    
    nome = factory.Sequence(lambda n: f'Badge Compra {n}')
    descricao = factory.Faker('sentence')
    tipo = 'COMPRA'
    custo_moedas = factory.Faker('random_int', min=100, max=1000)
    ativo = True


class UsuarioBadgeFactory(DjangoModelFactory):
    """Factory para badge conquistada por usuário"""
    
    class Meta:
        model = UsuarioBadge
    
    usuario = SubFactory(UsuarioFactory)
    badge = SubFactory(BadgeConquistaFactory)