from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from .models import Usuario


class ListarUsuariosTestCase(APITestCase):
    """Testes para a rota de listar usuários"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        # Criar admin
        self.admin = Usuario.objects.create_user(
            username='admin_teste',
            email='admin@ufrpe.br',
            password='admin123',
            is_staff=True
        )
        
        # Criar usuário comum
        self.usuario = Usuario.objects.create_user(
            username='usuario_teste',
            email='usuario@ufrpe.br',
            password='user123'
        )
        
        # Criar outro usuário
        self.usuario2 = Usuario.objects.create_user(
            username='usuario2_teste',
            email='usuario2@ufrpe.br',
            password='user123',
            is_active=False
        )
    
    def test_listar_usuarios_sem_autenticacao(self):
        """Usuários não autenticados não podem listar usuários"""
        url = reverse('listar-usuarios')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_listar_usuarios_usuario_comum_negado(self):
        """Usuários comuns não podem listar usuários"""
        self.client.force_authenticate(user=self.usuario)
        url = reverse('listar-usuarios')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_listar_usuarios_admin_permitido(self):
        """Admins podem listar usuários"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('listar-usuarios')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # 2 usuários + 1 admin
    
    def test_filtro_is_active(self):
        """Testar filtro por status ativo"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('listar-usuarios')
        
        # Listar apenas ativos
        response = self.client.get(url, {'is_active': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # admin e usuario (usuario2 está inativo)
        
        # Listar apenas inativos
        response = self.client.get(url, {'is_active': 'false'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # usuario2
    
    def test_filtro_is_staff(self):
        """Testar filtro por admin"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('listar-usuarios')
        
        # Listar apenas admins
        response = self.client.get(url, {'is_staff': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # apenas admin
        
        # Listar apenas usuários comuns
        response = self.client.get(url, {'is_staff': 'false'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # usuario e usuario2
    
    def test_busca_por_username(self):
        """Testar busca por username"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('listar-usuarios')
        response = self.client.get(url, {'search': 'usuario_teste'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class DeletarUsuarioTestCase(APITestCase):
    """Testes para a rota de deletar usuários"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.admin = Usuario.objects.create_user(
            username='admin_teste',
            email='admin@ufrpe.br',
            password='admin123',
            is_staff=True
        )
        
        self.superuser = Usuario.objects.create_user(
            username='super_teste',
            email='super@ufrpe.br',
            password='super123',
            is_staff=True,
            is_superuser=True
        )
        
        self.usuario = Usuario.objects.create_user(
            username='usuario_teste',
            email='usuario@ufrpe.br',
            password='user123'
        )
        
        self.admin2 = Usuario.objects.create_user(
            username='admin2_teste',
            email='admin2@ufrpe.br',
            password='admin123',
            is_staff=True
        )
    
    def test_deletar_sem_autenticacao(self):
        """Usuários não autenticados não podem deletar"""
        url = reverse('deletar-usuario', kwargs={'id': self.usuario.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_deletar_usuario_comum_negado(self):
        """Usuários comuns não podem deletar outros usuários"""
        self.client.force_authenticate(user=self.usuario)
        url = reverse('deletar-usuario', kwargs={'id': self.admin.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_deletar_usuario_comum(self):
        """Admin pode deletar usuário comum"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('deletar-usuario', kwargs={'id': self.usuario.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Usuario.objects.filter(id=self.usuario.id).exists())
    
    def test_admin_nao_pode_deletar_a_si_mesmo(self):
        """Admin não pode deletar sua própria conta"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('deletar-usuario', kwargs={'id': self.admin.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Usuario.objects.filter(id=self.admin.id).exists())
    
    def test_admin_nao_pode_deletar_outro_admin(self):
        """Admin comum não pode deletar outro admin"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('deletar-usuario', kwargs={'id': self.admin2.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Usuario.objects.filter(id=self.admin2.id).exists())
    
    def test_superuser_pode_deletar_admin(self):
        """Superuser pode deletar outro admin"""
        self.client.force_authenticate(user=self.superuser)
        url = reverse('deletar-usuario', kwargs={'id': self.admin2.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Usuario.objects.filter(id=self.admin2.id).exists())


class AtualizarUsuarioTestCase(APITestCase):
    """Testes para a rota de atualizar usuários"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.admin = Usuario.objects.create_user(
            username='admin_teste',
            email='admin@ufrpe.br',
            password='admin123',
            is_staff=True
        )
        
        self.superuser = Usuario.objects.create_user(
            username='super_teste',
            email='super@ufrpe.br',
            password='super123',
            is_staff=True,
            is_superuser=True
        )
        
        self.usuario = Usuario.objects.create_user(
            username='usuario_teste',
            email='usuario@ufrpe.br',
            password='user123'
        )
    
    def test_atualizar_sem_autenticacao(self):
        """Usuários não autenticados não podem atualizar"""
        url = reverse('atualizar-usuario', kwargs={'id': self.usuario.id})
        response = self.client.patch(url, {'saldo_moedas': 100})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_admin_promover_usuario(self):
        """Admin pode promover usuário para admin"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('atualizar-usuario', kwargs={'id': self.usuario.id})
        response = self.client.patch(url, {'is_staff': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que o usuário foi promovido
        usuario_atualizado = Usuario.objects.get(id=self.usuario.id)
        self.assertTrue(usuario_atualizado.is_staff)
    
    def test_admin_nao_pode_alterar_seu_proprio_status(self):
        """Admin não pode alterar seu próprio status de admin"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('atualizar-usuario', kwargs={'id': self.admin.id})
        response = self.client.patch(url, {'is_staff': False})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_admin_desativar_usuario(self):
        """Admin pode desativar um usuário"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('atualizar-usuario', kwargs={'id': self.usuario.id})
        response = self.client.patch(url, {'is_active': False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        usuario_atualizado = Usuario.objects.get(id=self.usuario.id)
        self.assertFalse(usuario_atualizado.is_active)
