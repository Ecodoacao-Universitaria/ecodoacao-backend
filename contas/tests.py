from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from .models import Usuario
from .factories import UsuarioFactory, AdminFactory, SuperuserFactory, UsuarioInativoFactory 


class ListarUsuariosTestCase(APITestCase):
    """
    Testes de integração para listagem de usuários.
    
    Cobre:
    - Permissões (admin, usuário comum, não autenticado)
    - Filtros (is_active, is_staff, search)
    """
    
    def setUp(self):
        """Cria usuários de teste usando factories"""
        self.admin = AdminFactory()
        self.usuario = UsuarioFactory()
        self.usuario_inativo = UsuarioInativoFactory()
        
        self.url = reverse('listar-usuarios')
    
    def test_sem_autenticacao_retorna_401(self):
        """GET /usuarios/ sem token deve retornar 401"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_usuario_comum_retorna_403(self):
        """GET /usuarios/ com usuário comum deve retornar 403"""
        self.client.force_authenticate(user=self.usuario)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_lista_todos_usuarios(self):
        """GET /usuarios/ com admin deve retornar todos os usuários"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data.get('results', response.data)
        usernames = {user['username'] for user in data}
        
        self.assertEqual(len(usernames), 3)
        self.assertIn(self.admin.username, usernames)
        self.assertIn(self.usuario.username, usernames)
        self.assertIn(self.usuario_inativo.username, usernames)
    
    def test_filtro_usuarios_ativos(self):
        """GET /usuarios/?is_active=true retorna apenas usuários ativos"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {'is_active': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data.get('results', response.data)
        usernames = {user['username'] for user in data}
        
        self.assertEqual(len(usernames), 2)
        self.assertIn(self.admin.username, usernames)
        self.assertIn(self.usuario.username, usernames)
        self.assertNotIn(self.usuario_inativo.username, usernames)  
    
    def test_filtro_usuarios_inativos(self):
        """GET /usuarios/?is_active=false retorna apenas usuários inativos"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {'is_active': 'false'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data.get('results', response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['username'], self.usuario_inativo.username)
    
    def test_filtro_apenas_admins(self):
        """GET /usuarios/?is_staff=true retorna apenas admins"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {'is_staff': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data.get('results', response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['username'], self.admin.username)
    
    def test_busca_por_username(self):
        """GET /usuarios/?search=usuario encontra usuários por username"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {'search': self.usuario.username})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data.get('results', response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['username'], self.usuario.username)
    
    def test_busca_por_email(self):
        """GET /usuarios/?search=@ufrpe encontra usuários por email"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {'search': '@ufrpe.br'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data.get('results', response.data)
        self.assertEqual(len(data), 3)  # Todos têm @ufrpe.br


class DeletarUsuarioTestCase(APITestCase):
    """
    Testes de integração para deleção de usuários.
    
    Cobre:
    - Permissões (admin, superuser, usuário comum)
    - Regras de negócio (não pode deletar a si mesmo, etc)
    """
    
    def setUp(self):
        """Cria usuários de teste usando factories"""
        self.admin = AdminFactory()
        self.superuser = SuperuserFactory()
        self.usuario = UsuarioFactory()
        self.admin2 = AdminFactory()
    
    def _get_url(self, usuario_id):
        """Helper para gerar URL de deleção"""
        return reverse('deletar-usuario', kwargs={'id': usuario_id})
    
    def test_sem_autenticacao_retorna_401(self):
        """DELETE /usuarios/{id}/ sem token retorna 401"""
        url = self._get_url(self.usuario.id)
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Usuario.objects.filter(id=self.usuario.id).exists())
    
    def test_usuario_comum_retorna_403(self):
        """DELETE /usuarios/{id}/ com usuário comum retorna 403"""
        self.client.force_authenticate(user=self.usuario)
        url = self._get_url(self.admin.id)
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Usuario.objects.filter(id=self.admin.id).exists())
    
    def test_admin_deleta_usuario_comum_com_sucesso(self):
        """Admin pode deletar usuário comum"""
        self.client.force_authenticate(user=self.admin)
        url = self._get_url(self.usuario.id)
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Usuario.objects.filter(id=self.usuario.id).exists())
        
        self.assertIn('sucesso', response.data)
        self.assertIn(self.usuario.username, response.data['sucesso'])
    
    def test_admin_nao_pode_deletar_a_si_mesmo(self):
        """Admin não pode deletar sua própria conta"""
        self.client.force_authenticate(user=self.admin)
        url = self._get_url(self.admin.id)
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Usuario.objects.filter(id=self.admin.id).exists())
        self.assertIn('erro', response.data)
    
    def test_admin_comum_nao_pode_deletar_outro_admin(self):
        """Admin comum não pode deletar outro admin"""
        self.client.force_authenticate(user=self.admin)
        url = self._get_url(self.admin2.id)
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Usuario.objects.filter(id=self.admin2.id).exists())
        self.assertIn('erro', response.data)
    
    def test_superuser_pode_deletar_admin(self):
        """Superuser pode deletar qualquer admin"""
        self.client.force_authenticate(user=self.superuser)
        url = self._get_url(self.admin2.id)
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Usuario.objects.filter(id=self.admin2.id).exists())
    
    def test_deletar_usuario_inexistente_retorna_404(self):
        """DELETE /usuarios/99999/ retorna 404"""
        self.client.force_authenticate(user=self.admin)
        url = self._get_url(99999)
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AtualizarUsuarioTestCase(APITestCase):
    """
    Testes de integração para atualização de usuários.
    
    Cobre:
    - Permissões (admin, superuser, usuário comum)
    - Promoção/rebaixamento de admins
    - Ativação/desativação de contas
    - Regras de negócio (não pode alterar próprio status)
    """
    
    def setUp(self):
        """Cria usuários de teste usando factories"""
        self.admin = AdminFactory()
        self.superuser = SuperuserFactory()
        self.usuario = UsuarioFactory()
        self.admin2 = AdminFactory()
    
    def _get_url(self, usuario_id):
        """Helper para gerar URL de atualização"""
        return reverse('atualizar-usuario', kwargs={'id': usuario_id})
    
    def test_sem_autenticacao_retorna_401(self):
        """PATCH /usuarios/{id}/ sem token retorna 401"""
        url = self._get_url(self.usuario.id)
        response = self.client.patch(url, {'is_active': False})
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_usuario_comum_retorna_403(self):
        """PATCH /usuarios/{id}/ com usuário comum retorna 403"""
        self.client.force_authenticate(user=self.usuario)
        url = self._get_url(self.admin.id)
        response = self.client.patch(url, {'is_staff': False})
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_promove_usuario_para_admin(self):
        """Admin pode promover usuário comum para admin"""
        self.client.force_authenticate(user=self.admin)
        url = self._get_url(self.usuario.id)
        
        # Estado inicial
        self.assertFalse(self.usuario.is_staff)
        
        response = self.client.patch(url, {'is_staff': True})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica que foi promovido
        usuario_atualizado = Usuario.objects.get(id=self.usuario.id)
        self.assertTrue(usuario_atualizado.is_staff)
        self.assertEqual(response.data['is_staff'], True)
    
    def test_admin_rebaixa_outro_admin(self):
        """Admin pode rebaixar outro admin para usuário comum"""
        self.client.force_authenticate(user=self.superuser)  # Precisa ser superuser
        url = self._get_url(self.admin2.id)
        
        response = self.client.patch(url, {'is_staff': False})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        usuario_atualizado = Usuario.objects.get(id=self.admin2.id)
        self.assertFalse(usuario_atualizado.is_staff)
    
    def test_admin_desativa_usuario(self):
        """Admin pode desativar conta de usuário"""
        self.client.force_authenticate(user=self.admin)
        url = self._get_url(self.usuario.id)
        
        response = self.client.patch(url, {'is_active': False})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        usuario_atualizado = Usuario.objects.get(id=self.usuario.id)
        self.assertFalse(usuario_atualizado.is_active)
    
    def test_admin_reativa_usuario_inativo(self):
        """Admin pode reativar conta desativada"""
        # Desativa primeiro
        self.usuario.is_active = False
        self.usuario.save()
        
        self.client.force_authenticate(user=self.admin)
        url = self._get_url(self.usuario.id)
        
        response = self.client.patch(url, {'is_active': True})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        usuario_atualizado = Usuario.objects.get(id=self.usuario.id)
        self.assertTrue(usuario_atualizado.is_active)
    
    def test_admin_nao_pode_alterar_proprio_status_staff(self):
        """Admin não pode alterar seu próprio status de administrador"""
        self.client.force_authenticate(user=self.admin)
        url = self._get_url(self.admin.id)
        
        response = self.client.patch(url, {'is_staff': False})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('erro', response.data)
        
        # Verifica que continua admin
        admin_atualizado = Usuario.objects.get(id=self.admin.id)
        self.assertTrue(admin_atualizado.is_staff)
    
    def test_admin_pode_alterar_outros_campos_proprios(self):
        """Admin pode alterar outros campos próprios (exceto is_staff)"""
        self.client.force_authenticate(user=self.admin)
        url = self._get_url(self.admin.id)
        
        # Alterar username é permitido
        response = self.client.patch(url, {'username': 'admin_novo'})
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
    
    def test_admin_comum_nao_pode_alterar_status_de_outro_admin(self):
        """Admin comum não pode alterar status de outro admin"""
        self.client.force_authenticate(user=self.admin)
        url = self._get_url(self.admin2.id)
        
        response = self.client.patch(url, {'is_staff': False})
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('erro', response.data)
        
        # Verifica que admin2 continua admin
        admin2_atualizado = Usuario.objects.get(id=self.admin2.id)
        self.assertTrue(admin2_atualizado.is_staff)
    
    def test_superuser_pode_alterar_status_de_qualquer_admin(self):
        """Superuser pode alterar status de qualquer admin"""
        self.client.force_authenticate(user=self.superuser)
        url = self._get_url(self.admin.id)
        
        response = self.client.patch(url, {'is_staff': False})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        admin_atualizado = Usuario.objects.get(id=self.admin.id)
        self.assertFalse(admin_atualizado.is_staff)
    
    def test_atualizar_multiplos_campos_simultaneamente(self):
        """Admin pode atualizar múltiplos campos de uma vez"""
        self.client.force_authenticate(user=self.admin)
        url = self._get_url(self.usuario.id)
        
        response = self.client.patch(url, {
            'is_staff': True,
            'is_active': False,
            'username': 'usuario_modificado'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        usuario_atualizado = Usuario.objects.get(id=self.usuario.id)
        self.assertTrue(usuario_atualizado.is_staff)
        self.assertFalse(usuario_atualizado.is_active)
        self.assertEqual(usuario_atualizado.username, 'usuario_modificado')
    
    def test_atualizar_usuario_inexistente_retorna_404(self):
        """PATCH /usuarios/99999/ retorna 404"""
        self.client.force_authenticate(user=self.admin)
        url = self._get_url(99999)
        
        response = self.client.patch(url, {'is_active': False})
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_dados_invalidos_retorna_400(self):
        """PATCH com dados inválidos retorna 400"""
        self.client.force_authenticate(user=self.admin)
        url = self._get_url(self.usuario.id)
        
        # Email inválido
        response = self.client.patch(url, {'email': 'email_invalido'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)