from django.test import TestCase
from contas.serializers import CadastroSerializer


#Teste unitario do RF01 - Cadastro de Usuário com e-mail institucional
#feito por : Juarez Lopes
class Cadastro_TesteUnitario(TestCase):
  

    def test_cadastro_email_institucional_valido(self):
        
        data = {
            'username': 'guilherme',
            'email': 'guilherme@ufrpe.br',
            'password': '@teste123'
        }
        
        # Verifica se o serializer aceita o e-mail institucional
        serializer = CadastroSerializer(data=data)
        self.assertTrue(serializer.is_valid(), f"Deveria aceitar: {serializer.errors}")



    def test_cadastro_email_externo_invalido(self):
        
        data = {
            'username': 'guilherme2',
            'email': 'guilherme2@hotmail.com',
            'password': '@teste123'
        }
        serializer = CadastroSerializer(data=data)
        
      
        self.assertFalse(serializer.is_valid(), "Não deve aceitar e-mail externo.")
        
        # Verifica se o erro está na chave 'email' e se a mensagem é a esperada
        self.assertIn('email', serializer.errors)
        self.assertIn('institucional da UFRPE', str(serializer.errors['email'][0]))