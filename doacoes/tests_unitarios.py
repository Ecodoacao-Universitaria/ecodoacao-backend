from django.test import TestCase
from rest_framework.exceptions import ValidationError
from doacoes.models import UsuarioBadge
from doacoes.services import BadgeService
from contas.factories import UsuarioFactory
from doacoes.factories import BadgeCompraFactory
from doacoes.models import Doacao
from doacoes.factories import DoacaoPendenteFactory, TipoDoacaoFactory
from contas.factories import AdminFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from doacoes.serializers import CriarDoacaoSerializer, ValidarDoacaoSerializer
from doacoes.models import TipoDoacao
from io import BytesIO
from PIL import Image


#Teste unitaio do RF04 - Gamificação - Compra de Badges com Moedas
#feito por : Guilherme Oliveira
class Gamificacao_TesteUnitario(TestCase):
  
    def setUp(self):

        self.usuario = UsuarioFactory(saldo_moedas=0)
        self.badge = BadgeCompraFactory(custo_moedas=50)

    def test_compra_badge_com_saldo_suficiente(self):
 
        self.usuario.saldo_moedas = 100
        self.usuario.save()

        resultado = BadgeService.comprar_badge(self.usuario, self.badge.id)

        self.assertTrue(resultado['sucesso'])
        
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.saldo_moedas, 50, "Deve descontar 50 moedas")
        
        possui_badge = UsuarioBadge.objects.filter(usuario=self.usuario, badge=self.badge).exists()
        self.assertTrue(possui_badge, "O usuário deve possuir o badge")

    def test_tentativa_compra_sem_saldo(self):

        self.usuario.saldo_moedas = 10
        self.usuario.save()

        
        try:
            BadgeService.comprar_badge(self.usuario, self.badge.id)
            falhou = False 
        except Exception:
            falhou = True
            
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.saldo_moedas, 10, "O saldo não deve mudar")
        
        possui_badge = UsuarioBadge.objects.filter(usuario=self.usuario, badge=self.badge).exists()
        self.assertFalse(possui_badge, "Não deve criar o registro de badge")





#teste unitario do RF03 - Validação de Doações - Admin aprova ou recusa doações
#feito por :  Leonardo Demetrio
class Admin_Validacao_TestUnitario(TestCase):

    def setUp(self):
        self.admin = AdminFactory() 
        self.tipo = TipoDoacaoFactory(moedas_atribuidas=100)
        
    
        self.doador = UsuarioFactory(saldo_moedas=0)
        
        self.doacao = DoacaoPendenteFactory(
            doador=self.doador,
            tipo_doacao=self.tipo,
            evidencia_foto='placeholder.jpg'
        )

    def test_aprovar_doacao(self):
       
        self.doacao.aprovar(self.admin)
        
        BadgeService.premiar_doacao_aprovada(self.doacao)
 
        self.assertEqual(self.doacao.status, 'APROVADA')
        
        self.doador.refresh_from_db()
        self.assertEqual(self.doador.saldo_moedas, 100, "Deveria creditar 100 moedas no saldo.")

    def test_rejeicao_vazia(self):

        data = {
            'status': 'RECUSADA',
            'motivo_recusa': '' 
        }
        
        serializer = ValidarDoacaoSerializer(data=data)
        
        # Verifica se o serializer rejeita a rejeição sem motivo
        self.assertFalse(serializer.is_valid(), "Não deve aceitar rejeição sem motivo.")
        self.assertIn('motivo_recusa', serializer.errors)




#Teste unitario do RF02 - Submissão de Doação - Envio com evidência obrigatória
#feito por : Rodrigo Galvão
class Doacao_Submissao_TestUnitario(TestCase):
    
    def setUp(self):
        
        self.tipo = TipoDoacao.objects.create(nome="Eletrônico", moedas_atribuidas=50)

    def _criar_imagem_falsa(self):
        
        arquivo = BytesIO()
        img = Image.new('RGB', (100, 100), color='red')
        img.save(arquivo, format='JPEG')
        arquivo.seek(0)
        return SimpleUploadedFile("teste.jpg", arquivo.read(), content_type="image/jpeg")
    
    def test_doacao_com_foto_valida(self):
        
        imagem = self._criar_imagem_falsa()
        
        data = {
            'tipo_doacao': self.tipo.id,
            'descricao': 'Um teclado antigo',
            'evidencia_foto': imagem
        }
        
        # Verifica se o serializer aceita doação com foto
        serializer = CriarDoacaoSerializer(data=data)
        self.assertTrue(serializer.is_valid(), f"Deveria aceitar doação com foto: {serializer.errors}")

    def test_doacao_sem_foto(self):
        
        data = {
            'tipo_doacao': self.tipo.id,
            'descricao': 'Doação sem prova'          
        }
        
        serializer = CriarDoacaoSerializer(data=data)
        
        # Verifica se o serializer rejeita doação sem foto
        self.assertFalse(serializer.is_valid(), "Não deve aceitar doação sem foto")
        self.assertIn('evidencia_foto', serializer.errors, "Deve exigir o campo evidencia_foto")