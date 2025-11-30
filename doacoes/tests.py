from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO

from .models import Doacao, TipoDoacao, Badge, UsuarioBadge
from contas.models import Usuario
from contas.factories import UsuarioFactory, AdminFactory
from .factories import (
    TipoDoacaoFactory,
    DoacaoPendenteFactory,
    DoacaoAprovadaFactory,
    DoacaoRecusadaFactory,
    BadgeConquistaFactory,
    BadgeCompraFactory,
    UsuarioBadgeFactory
)

def _err_field(resp_data, field):
    if field in resp_data:
        return resp_data[field]
    return resp_data.get('detalhes', {}).get(field)


def criar_imagem_teste():
    """Helper para criar imagem de teste"""
    imagem = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    imagem.save(buffer, format='JPEG')
    buffer.seek(0)
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=buffer.read(),
        content_type='image/jpeg'
    )


# ============================================================================
# TESTES DE SUBMISSÃO DE DOAÇÃO
# ============================================================================

class SubmeterDoacaoTestCase(APITestCase):
    """
    Testes para submissão de doações pelos usuários.
    
    Cobre:
    - Autenticação
    - Validação de dados
    - Criação de doação
    """
    
    def setUp(self):
        self.usuario = UsuarioFactory()
        self.tipo_doacao = TipoDoacaoFactory(nome='Papel', moedas_atribuidas=50)
        self.url = reverse('doacao_submeter')
    
    def test_sem_autenticacao_retorna_401(self):
        """POST /doacoes/submeter/ sem token retorna 401"""
        response = self.client.post(self.url, {})
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_submeter_doacao_com_sucesso(self):
        """Usuário autenticado pode submeter doação"""
        self.client.force_authenticate(user=self.usuario)
        
        imagem = criar_imagem_teste()
        
        data = {
            'tipo_doacao': self.tipo_doacao.id,
            'evidencia_foto': imagem
        }
        
        response = self.client.post(self.url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'PENDENTE')
        self.assertEqual(response.data['tipo_doacao'], 'Papel')
        
        # Verifica que foi salva no banco
        self.assertEqual(Doacao.objects.count(), 1)
        doacao = Doacao.objects.first()
        self.assertEqual(doacao.doador, self.usuario)
        self.assertEqual(doacao.tipo_doacao, self.tipo_doacao)
    
    def test_submeter_sem_evidencia_retorna_400(self):
        self.client.force_authenticate(user=self.usuario)
        response = self.client.post(self.url, data={}, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(_err_field(response.data, 'evidencia_foto'), "Campo evidencia_foto deve estar em detalhes do erro")
    
    def test_submeter_tipo_inexistente_retorna_400(self):
        """POST com tipo_doacao inexistente retorna 400"""
        self.client.force_authenticate(user=self.usuario)
        
        imagem = criar_imagem_teste()
        
        data = {
            'tipo_doacao': 99999,
            'evidencia_foto': imagem
        }
        
        response = self.client.post(self.url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ============================================================================
# TESTES DE HISTÓRICO DE DOAÇÕES
# ============================================================================

class HistoricoDoacoesTestCase(APITestCase):
    """
    Testes para visualização do histórico de doações do usuário.
    
    Cobre:
    - Listagem apenas das próprias doações
    - Diferentes status
    """
    
    def setUp(self):
        self.usuario1 = UsuarioFactory()
        self.usuario2 = UsuarioFactory()
        self.admin = AdminFactory()
        
        # Doações do usuário1
        self.doacao_pendente = DoacaoPendenteFactory(doador=self.usuario1)
        self.doacao_aprovada = DoacaoAprovadaFactory(doador=self.usuario1)
        self.doacao_recusada = DoacaoRecusadaFactory(doador=self.usuario1)
        
        # Doação de outro usuário
        DoacaoPendenteFactory(doador=self.usuario2)
        
        self.url = reverse('doacao_historico')
    
    def test_sem_autenticacao_retorna_401(self):
        """GET /doacoes/historico/ sem token retorna 401"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_usuario_ve_apenas_proprias_doacoes(self):
        """Usuário vê apenas suas próprias doações"""
        self.client.force_authenticate(user=self.usuario1)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica que retornou 3 doações (do usuário1)
        data = response.data.get('results', response.data)
        self.assertEqual(len(data), 3)
        
        # Verifica que todas são do usuário1
        for doacao in data:
            self.assertIn(self.usuario1.username, doacao['doador'])
    
    def test_filtrar_por_status_pendente(self):
        """GET /doacoes/historico/?status=PENDENTE"""
        self.client.force_authenticate(user=self.usuario1)
        response = self.client.get(self.url, {'status': 'PENDENTE'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data.get('results', response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['status'], 'PENDENTE')
    
    def test_filtrar_por_status_aprovada(self):
        """GET /doacoes/historico/?status=APROVADA"""
        self.client.force_authenticate(user=self.usuario1)
        response = self.client.get(self.url, {'status': 'APROVADA'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data.get('results', response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['status'], 'APROVADA')


# ============================================================================
# TESTES DE LISTAGEM DE DOAÇÕES PENDENTES (ADMIN)
# ============================================================================

class AdminDoacoesPendentesTestCase(APITestCase):
    """
    Testes para listagem de doações pendentes por admins.
    
    Cobre:
    - Permissões (apenas admin)
    - Listagem de pendentes
    """
    
    def setUp(self):
        self.admin = AdminFactory()
        self.usuario = UsuarioFactory()
        
        self.doacao_pendente1 = DoacaoPendenteFactory()
        self.doacao_pendente2 = DoacaoPendenteFactory()
        DoacaoAprovadaFactory()  # Não deve aparecer
        
        self.url = reverse('admin_doacoes_pendentes')
    
    def test_sem_autenticacao_retorna_401(self):
        """GET /doacoes/admin/pendentes/ sem token retorna 401"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_usuario_comum_retorna_403(self):
        """GET /doacoes/admin/pendentes/ com usuário comum retorna 403"""
        self.client.force_authenticate(user=self.usuario)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_lista_doacoes_pendentes(self):
        """Admin vê todas as doações pendentes"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data.get('results', response.data)
        self.assertEqual(len(data), 2)
        
        # Verifica que todas são pendentes
        for doacao in data:
            self.assertEqual(doacao['status'], 'PENDENTE')


# ============================================================================
# TESTES DE VALIDAÇÃO DE DOAÇÃO (ADMIN)
# ============================================================================

class AdminValidarDoacaoTestCase(APITestCase):
    """
    Testes para aprovação/rejeição de doações por admins.
    
    Cobre:
    - Permissões
    - Aprovação (distribui moedas e badges)
    - Rejeição (exige motivo)
    """
    
    def setUp(self):
        self.admin = AdminFactory()
        self.usuario = UsuarioFactory(saldo_moedas=0)
        
        self.tipo_doacao = TipoDoacaoFactory(moedas_atribuidas=100)
        self.doacao_pendente = DoacaoPendenteFactory(
            doador=self.usuario,
            tipo_doacao=self.tipo_doacao
        )
        
        # Badge de conquista (1 doação)
        self.badge_iniciante = BadgeConquistaFactory(
            nome='🌱 Iniciante',
            criterio_doacoes=1
        )
    
    def _get_url(self, doacao_id):
        return reverse('admin_doacao_validar', kwargs={'pk': doacao_id})
    
    def test_sem_autenticacao_retorna_401(self):
        """PATCH /doacoes/admin/validar/{id}/ sem token retorna 401"""
        url = self._get_url(self.doacao_pendente.id)
        response = self.client.patch(url, {})
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_usuario_comum_retorna_403(self):
        """Usuário comum não pode validar doações"""
        usuario = UsuarioFactory()
        self.client.force_authenticate(user=usuario)
        
        url = self._get_url(self.doacao_pendente.id)
        response = self.client.patch(url, {'status': 'APROVADA'})
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_aprova_doacao_com_sucesso(self):
        """Admin aprova doação e usuário recebe moedas"""
        self.client.force_authenticate(user=self.admin)
        url = self._get_url(self.doacao_pendente.id)
        response = self.client.patch(url, {'status': 'APROVADA'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doacao = Doacao.objects.get(id=self.doacao_pendente.id)
        self.assertEqual(doacao.status, 'APROVADA')
        self.assertEqual(doacao.validado_por, self.admin)
        self.assertIsNotNone(doacao.data_validacao)
        usuario_atualizado = Usuario.objects.get(id=self.usuario.id)
        self.assertEqual(usuario_atualizado.saldo_moedas, 100)
        
        usuario_atualizado = Usuario.objects.get(id=self.usuario.id)
        self.assertEqual(usuario_atualizado.saldo_moedas, 100)
    
    def test_aprovar_doacao_atribui_badge_automaticamente(self):
        """Ao aprovar doação, badge de conquista é atribuída"""
        self.client.force_authenticate(user=self.admin)
        
        url = self._get_url(self.doacao_pendente.id)
        response = self.client.patch(url, {'status': 'APROVADA'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica que badge foi atribuída
        badge_conquistada = UsuarioBadge.objects.filter(
            usuario=self.usuario,
            badge=self.badge_iniciante
        ).exists()
        self.assertTrue(badge_conquistada)
    
    def test_admin_recusa_doacao_com_motivo(self):
        """Admin recusa doação com motivo"""
        self.client.force_authenticate(user=self.admin)
        url = self._get_url(self.doacao_pendente.id)
        response = self.client.patch(url, {
            'status': 'RECUSADA',
            'motivo_recusa': 'Evidência não corresponde ao tipo de doação'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doacao = Doacao.objects.get(id=self.doacao_pendente.id)
        self.assertEqual(doacao.status, 'RECUSADA')
        self.assertIsNotNull = self.assertIsNotNone(doacao.motivo_recusa)
        usuario_atualizado = Usuario.objects.get(id=self.usuario.id)
        self.assertEqual(usuario_atualizado.saldo_moedas, 0)
    
    def test_recusar_sem_motivo_retorna_400(self):
        """Recusar doação sem motivo retorna erro"""
        self.client.force_authenticate(user=self.admin)
        url = self._get_url(self.doacao_pendente.id)
        response = self.client.patch(url, {'status': 'RECUSADA'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(_err_field(response.data, 'motivo_recusa'))
    
    def test_validar_doacao_inexistente_retorna_404(self):
        """PATCH /doacoes/admin/validar/99999/ retorna 404"""
        self.client.force_authenticate(user=self.admin)
        
        url = self._get_url(99999)
        response = self.client.patch(url, {'status': 'APROVADA'})
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ============================================================================
# TESTES DE BADGES
# ============================================================================

class BadgeListarTestCase(APITestCase):
    """
    Testes para listagem de badges.
    
    Cobre:
    - Listagem geral
    - Minhas badges
    - Badges disponíveis para compra
    """
    
    def setUp(self):
        self.usuario = UsuarioFactory(saldo_moedas=1000)
        
        # Badges de conquista
        self.badge_conquista1 = BadgeConquistaFactory(criterio_doacoes=1)
        self.badge_conquista2 = BadgeConquistaFactory(criterio_doacoes=5)
        
        # Badges de compra
        self.badge_compra1 = BadgeCompraFactory(custo_moedas=500)
        self.badge_compra2 = BadgeCompraFactory(custo_moedas=800)
        
        # Usuário já possui uma badge
        UsuarioBadgeFactory(usuario=self.usuario, badge=self.badge_conquista1)
    
    def test_listar_todas_badges(self):
        """GET /badges/ lista todas badges ativas"""
        self.client.force_authenticate(user=self.usuario)
        
        url = reverse('badge-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data.get('results', response.data)
        self.assertEqual(len(data), 4)
    
    def test_listar_minhas_badges(self):
        """GET /badges/minhas-badges/ lista apenas badges conquistadas"""
        self.client.force_authenticate(user=self.usuario)
        
        url = reverse('badge-minhas-badges')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['badge']['id'], self.badge_conquista1.id)
    
    def test_listar_badges_disponiveis_para_compra(self):
        """GET /badges/disponiveis/ lista badges que posso comprar"""
        self.client.force_authenticate(user=self.usuario)
        
        url = reverse('badge-disponiveis')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Deve retornar apenas badges de COMPRA que o usuário não possui
        self.assertEqual(len(response.data), 2)
        for badge in response.data:
            self.assertEqual(badge['tipo'], 'COMPRA')


class BadgeComprarTestCase(APITestCase):
    """
    Testes para compra de badges com moedas.
    
    Cobre:
    - Compra bem-sucedida
    - Saldo insuficiente
    - Badge já possuída
    """
    
    def setUp(self):
        self.usuario_rico = UsuarioFactory(saldo_moedas=1000)
        self.usuario_pobre = UsuarioFactory(saldo_moedas=100)
        
        self.badge_cara = BadgeCompraFactory(custo_moedas=800)
        self.badge_barata = BadgeCompraFactory(custo_moedas=200)
    
    def test_comprar_badge_com_sucesso(self):
        """Usuário com saldo suficiente compra badge"""
        self.client.force_authenticate(user=self.usuario_rico)
        
        url = reverse('badge-comprar')
        response = self.client.post(url, {'badge_id': self.badge_cara.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['sucesso'])
        self.assertEqual(response.data['saldo_restante'], 200)
        
        # Verifica que badge foi atribuída
        badge_possui = UsuarioBadge.objects.filter(
            usuario=self.usuario_rico,
            badge=self.badge_cara
        ).exists()
        self.assertTrue(badge_possui)
        
        # Verifica que moedas foram debitadas
        usuario_atualizado = Usuario.objects.get(id=self.usuario_rico.id)
        self.assertEqual(usuario_atualizado.saldo_moedas, 200)
    
    def test_comprar_badge_sem_saldo_retorna_400(self):
        """Usuário sem saldo suficiente não pode comprar"""
        self.client.force_authenticate(user=self.usuario_pobre)
        url = reverse('badge-comprar')
        response = self.client.post(url, {'badge_id': self.badge_cara.id})
        self.assertEqual(response.status_code, 402)
        self.assertFalse(response.data['sucesso'])
        self.assertIn('insuficiente', response.data['mensagem'].lower())
    
    def test_comprar_badge_ja_possuida_retorna_400(self):
        """Não pode comprar badge que já possui"""
        UsuarioBadgeFactory(usuario=self.usuario_rico, badge=self.badge_barata)
        self.client.force_authenticate(user=self.usuario_rico)
        response = self.client.post(reverse('badge-comprar'), data={'badge_id': self.badge_barata.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['sucesso'])
        self.assertEqual(response.data.get('codigo'), 'JA_POSSUI_BADGE')
    
    def test_comprar_badge_inexistente_retorna_400(self):
        """Tentar comprar badge inexistente retorna erro"""
        self.client.force_authenticate(user=self.usuario_rico)
        
        url = reverse('badge-comprar')
        response = self.client.post(url, {'badge_id': 99999})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ============================================================================
# TESTES DE LISTAGEM DE TIPOS DE DOAÇÃO
# ============================================================================

class ListarTiposDoacaoTestCase(APITestCase):
    """
    Testes para listagem de tipos de doação.
    
    Cobre:
    - Autenticação
    - Listagem de tipos de doação
    - Ordenação por nome
    """
    
    def setUp(self):
        self.usuario = UsuarioFactory()
        
        # Criar tipos de doação em ordem aleatória para testar ordenação
        self.tipo_papel = TipoDoacaoFactory(nome='Papel', moedas_atribuidas=50)
        self.tipo_aluminio = TipoDoacaoFactory(nome='Alumínio', moedas_atribuidas=80)
        self.tipo_vidro = TipoDoacaoFactory(nome='Vidro', moedas_atribuidas=60)
        
        self.url = reverse('doacao_tipos')
    
    def test_sem_autenticacao_retorna_401(self):
        """GET /doacoes/tipos/ sem token retorna 401"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_listar_tipos_doacao_com_sucesso(self):
        """Usuário autenticado pode listar tipos de doação"""
        self.client.force_authenticate(user=self.usuario)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data.get('results', response.data)
        self.assertEqual(len(data), 3)
    
    def test_tipos_doacao_ordenados_por_nome(self):
        """Tipos de doação são retornados ordenados por nome"""
        self.client.force_authenticate(user=self.usuario)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data.get('results', response.data)
        nomes = [tipo['nome'] for tipo in data]
        
        # Verifica que estão em ordem alfabética
        self.assertEqual(nomes, sorted(nomes))