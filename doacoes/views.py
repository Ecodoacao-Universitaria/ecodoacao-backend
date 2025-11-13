from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Doacao
from .serializers import DoacaoSerializer, CriarDoacaoSerializer
from django.utils import timezone


@extend_schema(
    tags=['Admin - Doações'],
    summary='Listar doações pendentes',
    description='Lista todas as doações com status PENDENTE aguardando validação. Requer permissão de administrador.',
    responses={
        200: {
            'description': 'Lista de doações pendentes',
            'content': {
                'application/json': {
                    'example': {
                        'count': 2,
                        'next': None,
                        'previous': None,
                        'results': [
                            {
                                'id': 1,
                                'doador': {
                                    'id': 2,
                                    'username': 'joao123',
                                    'email': 'joao@example.com'
                                },
                                'tipo_doacao': {
                                    'id': 1,
                                    'nome': 'Garrafa PET',
                                    'moedas_atribuidas': 10
                                },
                                'quantidade': 5,
                                'descricao': 'Garrafas limpas e sem rótulo',
                                'foto_comprovante': 'http://localhost:8000/media/doacoes/foto1.jpg',
                                'status': 'PENDENTE',
                                'data_submissao': '2025-11-13T10:30:00Z',
                                'data_validacao': None,
                                'validado_por': None,
                                'motivo_recusa': None
                            }
                        ]
                    }
                }
            }
        },
        403: {
            'description': 'Sem permissão de administrador',
            'content': {
                'application/json': {
                    'example': {
                        'detail': 'Você não tem permissão para executar essa ação.'
                    }
                }
            }
        }
    }
)
class AdminDoacoesPendentesView(generics.ListAPIView):
  
    queryset = Doacao.objects.filter(status='PENDENTE')
    serializer_class = DoacaoSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Doacao.objects.filter(status='PENDENTE').order_by('data_submissao')
    
@extend_schema(
    tags=['Doações'],
    summary='Criar nova doação',
    description='Submete uma nova doação para validação. O usuário deve enviar foto comprovante, tipo de doação e quantidade.',
    request=CriarDoacaoSerializer,
    responses={
        201: {
            'description': 'Doação criada com sucesso',
            'content': {
                'application/json': {
                    'example': {
                        'id': 1,
                        'doador': {
                            'id': 2,
                            'username': 'joao123',
                            'email': 'joao@example.com'
                        },
                        'tipo_doacao': {
                            'id': 1,
                            'nome': 'Garrafa PET',
                            'moedas_atribuidas': 10
                        },
                        'quantidade': 5,
                        'descricao': 'Garrafas limpas e sem rótulo',
                        'foto_comprovante': 'http://localhost:8000/media/doacoes/foto1.jpg',
                        'status': 'PENDENTE',
                        'data_submissao': '2025-11-13T10:30:00Z'
                    }
                }
            }
        },
        400: {
            'description': 'Dados inválidos',
            'content': {
                'application/json': {
                    'example': {
                        'tipo_doacao': ['Este campo é obrigatório.'],
                        'quantidade': ['Certifique-se de que este valor seja maior ou igual a 1.']
                    }
                }
            }
        },
        401: {
            'description': 'Não autenticado',
            'content': {
                'application/json': {
                    'example': {
                        'detail': 'As credenciais de autenticação não foram fornecidas.'
                    }
                }
            }
        }
    }
)
class CriarDoacaoView(generics.CreateAPIView):
    queryset = Doacao.objects.all()
    serializer_class = CriarDoacaoSerializer
    permission_classes = [IsAuthenticated] 

    def perform_create(self, serializer):
        # Associa automaticamente o usuário logado como 'doador'
        serializer.save(doador=self.request.user)

@extend_schema(
    tags=['Admin - Doações'],
    summary='Validar doação (aprovar/recusar)',
    description='Valida uma doação pendente. Se aprovada, adiciona moedas ao usuário. Se recusada, requer motivo.',
    request={
        'application/json': {
            'type': 'object',
            'required': ['status'],
            'properties': {
                'status': {
                    'type': 'string',
                    'enum': ['APROVADA', 'RECUSADA'],
                    'description': 'Novo status da doação'
                },
                'motivo_recusa': {
                    'type': 'string',
                    'description': 'Motivo da recusa (obrigatório se status = RECUSADA)'
                }
            },
            'examples': [
                {
                    'name': 'Aprovar doação',
                    'summary': 'Aprova e credita moedas ao usuário',
                    'value': {
                        'status': 'APROVADA'
                    }
                },
                {
                    'name': 'Recusar doação',
                    'summary': 'Recusa com justificativa',
                    'value': {
                        'status': 'RECUSADA',
                        'motivo_recusa': 'Foto de baixa qualidade ou não corresponde ao tipo de doação'
                    }
                }
            ]
        }
    },
    responses={
        200: {
            'description': 'Doação validada com sucesso',
            'content': {
                'application/json': {
                    'examples': {
                        'aprovada': {
                            'summary': 'Doação aprovada',
                            'value': {
                                'id': 1,
                                'doador': {
                                    'id': 2,
                                    'username': 'joao123',
                                    'email': 'joao@example.com'
                                },
                                'tipo_doacao': {
                                    'id': 1,
                                    'nome': 'Garrafa PET',
                                    'moedas_atribuidas': 10
                                },
                                'quantidade': 5,
                                'status': 'APROVADA',
                                'data_validacao': '2025-11-13T11:00:00Z',
                                'validado_por': {
                                    'id': 1,
                                    'username': 'admin'
                                },
                                'motivo_recusa': None
                            }
                        },
                        'recusada': {
                            'summary': 'Doação recusada',
                            'value': {
                                'id': 1,
                                'status': 'RECUSADA',
                                'motivo_recusa': 'Foto de baixa qualidade',
                                'data_validacao': '2025-11-13T11:00:00Z',
                                'validado_por': {
                                    'id': 1,
                                    'username': 'admin'
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Erro de validação',
            'content': {
                'application/json': {
                    'examples': {
                        'ja_validada': {
                            'summary': 'Doação já validada',
                            'value': {'erro': 'Esta doação já foi validada.'}
                        },
                        'sem_motivo': {
                            'summary': 'Motivo obrigatório para recusa',
                            'value': {'erro': 'Motivo de recusa é obrigatório.'}
                        },
                        'status_invalido': {
                            'summary': 'Status inválido',
                            'value': {'erro': "Status inválido. Use 'APROVADA' ou 'RECUSADA'."}
                        }
                    }
                }
            }
        },
        403: {
            'description': 'Sem permissão de administrador',
            'content': {
                'application/json': {
                    'example': {
                        'detail': 'Você não tem permissão para executar essa ação.'
                    }
                }
            }
        },
        404: {
            'description': 'Doação não encontrada',
            'content': {
                'application/json': {
                    'example': {
                        'detail': 'Não encontrado.'
                    }
                }
            }
        }
    }
)
class AdminAtualizarDoacaoView(generics.RetrieveUpdateAPIView):
    queryset = Doacao.objects.all()
    serializer_class = DoacaoSerializer
    permission_classes = [IsAdminUser]  # Apenas administradores podem acessar esta view(is_staff=True)

    http_method_names = ['put', 'patch']  # Permitir apenas métodos put e patch

    def update(self, request, *args, **kwargs):

        doacao = self.get_object() # pega o objeto da doação a ser atualizada ex /api/doacoes/admin/validar/3/


        novo_status = request.data.get('status') # obtém o novo status do corpo do request

        if doacao.status != 'PENDENTE':
            return Response(
                {"erro": "Esta doação já foi validada."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if novo_status == 'APROVADA':
            doador = doacao.doador
            moedas_ganhas = doacao.tipo_doacao.moedas_atribuidas
            
            # Atualiza o saldo do usuário
            doador.saldo_moedas += moedas_ganhas
            doador.save()
            
            # Atualiza a doação
            doacao.status = 'APROVADA'

        elif novo_status == 'RECUSADA':
            motivo = request.data.get('motivo_recusa')

            if not motivo:
                return Response(
                    {"erro": "Motivo de recusa é obrigatório."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            doacao.status = 'RECUSADA'
            doacao.motivo_recusa = motivo

        else:
            return Response(
                {"erro": "Status inválido. Use 'APROVADA' ou 'RECUSADA'."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Salva as mudanças na doação
        doacao.validado_por = request.user
        doacao.data_validacao = timezone.now()
        doacao.save()
        
        return Response(DoacaoSerializer(doacao).data, status=status.HTTP_200_OK)
    
@extend_schema(
    tags=['Doações'],
    summary='Histórico de doações do usuário',
    description='Lista todas as doações do usuário autenticado ordenadas por data (mais recente primeiro)',
    responses={
        200: {
            'description': 'Histórico de doações',
            'content': {
                'application/json': {
                    'example': {
                        'count': 3,
                        'next': None,
                        'previous': None,
                        'results': [
                            {
                                'id': 3,
                                'tipo_doacao': {
                                    'id': 1,
                                    'nome': 'Garrafa PET',
                                    'moedas_atribuidas': 10
                                },
                                'quantidade': 5,
                                'status': 'APROVADA',
                                'data_submissao': '2025-11-13T10:30:00Z',
                                'data_validacao': '2025-11-13T11:00:00Z',
                                'motivo_recusa': None
                            },
                            {
                                'id': 2,
                                'tipo_doacao': {
                                    'id': 2,
                                    'nome': 'Lata de Alumínio',
                                    'moedas_atribuidas': 5
                                },
                                'quantidade': 10,
                                'status': 'RECUSADA',
                                'data_submissao': '2025-11-12T15:00:00Z',
                                'data_validacao': '2025-11-12T16:00:00Z',
                                'motivo_recusa': 'Foto de baixa qualidade'
                            },
                            {
                                'id': 1,
                                'tipo_doacao': {
                                    'id': 1,
                                    'nome': 'Garrafa PET',
                                    'moedas_atribuidas': 10
                                },
                                'quantidade': 3,
                                'status': 'PENDENTE',
                                'data_submissao': '2025-11-11T09:00:00Z',
                                'data_validacao': None,
                                'motivo_recusa': None
                            }
                        ]
                    }
                }
            }
        },
        401: {
            'description': 'Não autenticado',
            'content': {
                'application/json': {
                    'example': {
                        'detail': 'As credenciais de autenticação não foram fornecidas.'
                    }
                }
            }
        }
    }
)
class HistoricoDoacoesView(generics.ListAPIView):

    serializer_class = DoacaoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filtra o queryset para retornar apenas doações do usuário que está fazendo o request.
        return Doacao.objects.filter(doador=self.request.user).order_by('-data_submissao')