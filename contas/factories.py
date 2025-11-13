"""
Factories para criação de dados de teste do app contas.

Uso:
    from contas.factories import UsuarioFactory, AdminFactory
    
    # Criar um usuário comum
    usuario = UsuarioFactory()
    
    # Criar um admin
    admin = AdminFactory()
    
    # Criar 10 usuários de uma vez
    usuarios = UsuarioFactory.create_batch(10)
    
    # Criar com dados específicos
    usuario = UsuarioFactory(email='especifico@teste.com', username='joao')
"""

import factory
from factory.django import DjangoModelFactory
from .models import Usuario


class UsuarioFactory(DjangoModelFactory):
    """
    Factory para criar usuários de teste.
    
    Gera automaticamente:
    - username único (usuario_1, usuario_2, ...)
    - email único baseado no username
    - senha padrão 'senha123' (já com hash)
    """
    
    class Meta:
        model = Usuario
    
    username = factory.Sequence(lambda n: f'usuario_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@ufrpe.br')
    password = factory.PostGenerationMethodCall('set_password', 'senha123')
    is_active = True
    is_staff = False
    is_superuser = False


class AdminFactory(UsuarioFactory):
    """
    Factory para criar administradores.
    
    Herda de UsuarioFactory mas com is_staff=True.
    """
    username = factory.Sequence(lambda n: f'admin_{n}')
    is_staff = True


class SuperuserFactory(UsuarioFactory):
    """
    Factory para criar superusuários.
    
    Herda de UsuarioFactory mas com is_staff=True e is_superuser=True.
    """
    username = factory.Sequence(lambda n: f'super_{n}')
    is_staff = True
    is_superuser = True


class UsuarioInativoFactory(UsuarioFactory):
    """
    Factory para criar usuários inativos.
    """
    username = factory.Sequence(lambda n: f'inativo_{n}')
    is_active = False