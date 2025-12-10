# 🌱 EcoDoação - Backend

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![DRF](https://img.shields.io/badge/DRF-3.16-red.svg)](https://www.django-rest-framework.org/)

API REST desenvolvida em Django REST Framework para gerenciamento de doações universitárias, focada em conectar doadores e receptores em ambiente acadêmico.

## 📋 Sobre o Projeto

O **EcoDoação Backend** é uma API robusta que permite:

- 🔐 **Autenticação segura** com JWT (JSON Web Tokens)
- 👥 **Gerenciamento de usuários** com diferentes níveis de permissão
- 📦 **Sistema de doações** completo com status e categorias
- 🏆 **Sistema de badges** para gamificação
- 📸 **Upload de imagens** para doações (Cloudinary/S3)
- 📊 **Documentação automática** com OpenAPI/Swagger
- ✅ **Testes automatizados** com alta cobertura

## 🚀 Tecnologias

- **Python 3.11**
- **Django 5.2**
- **Django REST Framework 3.16**
- **PostgreSQL 15**
- **Docker & Docker Compose**
- **JWT Authentication** (djangorestframework-simplejwt)
- **drf-spectacular** (documentação OpenAPI/Swagger)
- **Coverage.py** (cobertura de testes)
- **Cloudinary** (armazenamento de mídia)

---

## 🧰 Pré-requisitos

- **Docker** e **Docker Compose** instalados ([Guia de Instalação](https://docs.docker.com/get-docker/))
- **Git** para clonar o repositório
- **Python 3.11+** (para desenvolvimento local sem Docker)
- **PostgreSQL 15+** (para desenvolvimento local sem Docker)

---

## 📦 Instalação e Uso

### Com Docker (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/Ecodoacao-Universitaria/ecodoacao-backend.git
cd ecodoacao-backend

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# 3. Construa e inicie os containers
docker compose up --build

# 4. Em outro terminal, execute as migrações (primeira vez)
docker compose exec backend python manage.py migrate

# 5. Crie um superusuário (opcional)
docker compose exec backend python manage.py createsuperuser

# 6. Acesse a API
# - API: http://localhost:8000/api/
# - Swagger UI: http://localhost:8000/api/schema/swagger-ui/
# - ReDoc: http://localhost:8000/api/schema/redoc/
# - Admin: http://localhost:8000/admin/
```

### Desenvolvimento Local (Sem Docker)

```bash
# 1. Clone o repositório
git clone https://github.com/Ecodoacao-Universitaria/ecodoacao-backend.git
cd ecodoacao-backend

# 2. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instale as dependências
pip install -r requirements.txt
# Para desenvolvimento (inclui ferramentas de teste e qualidade)
pip install -r requirements-dev.txt

# 4. Configure o arquivo .env
cp .env.example .env
# Edite o .env com suas configurações do PostgreSQL local

# 5. Execute as migrações
python manage.py migrate

# 6. Crie um superusuário
python manage.py createsuperuser

# 7. Inicie o servidor de desenvolvimento
python manage.py runserver

# 8. Acesse: http://localhost:8000/api/
```

---

## ⚙️ Variáveis de Ambiente

Configure as seguintes variáveis no arquivo `.env`:

| Variável | Descrição | Exemplo | Obrigatório |
|----------|-----------|---------|-------------|
| `DEBUG` | Modo de depuração | `True` ou `False` | Sim |
| `SECRET_KEY` | Chave secreta do Django | `django-insecure-xxx` | Sim (produção) |
| `DB_ENGINE` | Engine do banco de dados | `django.db.backends.postgresql` | Sim |
| `DB_NAME` | Nome do banco de dados | `doacoes_db` | Sim |
| `DB_USER` | Usuário do banco | `postgres` | Sim |
| `DB_PASSWORD` | Senha do banco | `postgres123` | Sim |
| `DB_HOST` | Host do banco | `localhost` ou `db` | Sim |
| `DB_PORT` | Porta do banco | `5432` | Sim |
| `DATABASE_URL` | URL completa do banco (alternativa) | `postgresql://user:pass@host/db` | Não |
| `ALLOWED_HOSTS` | Hosts permitidos (separados por vírgula) | `localhost,127.0.0.1` | Sim |
| `CORS_ALLOWED_ORIGINS` | Origens CORS permitidas | `http://localhost:3000` | Sim |
| `AWS_ACCESS_KEY_ID` | Chave de acesso AWS S3 | `AKIAXXXXXXXX` | Não |
| `AWS_SECRET_ACCESS_KEY` | Chave secreta AWS S3 | `xxxxxxxx` | Não |
| `AWS_STORAGE_BUCKET_NAME` | Nome do bucket S3 | `my-bucket` | Não |
| `AWS_S3_REGION_NAME` | Região do S3 | `sa-east-1` | Não |

> 💡 **Dica**: Gere uma SECRET_KEY segura com:  
> `python -c "import secrets; print(secrets.token_urlsafe(50))"`

---

## 📁 Estrutura do Projeto

```
ecodoacao-backend/
├── 📁 core/              # Configurações principais do Django
│   ├── settings.py       # Configurações do projeto
│   ├── urls.py           # URLs principais
│   ├── validators.py     # Validadores customizados
│   └── exceptions.py     # Tratamento de exceções
├── 📁 contas/            # App de autenticação e usuários
│   ├── models.py         # Modelo de usuário customizado
│   ├── views.py          # Views de autenticação
│   ├── serializers.py    # Serializers de usuário
│   ├── urls.py           # Rotas de contas
│   └── tests.py          # Testes de autenticação
├── 📁 doacoes/           # App principal de doações
│   ├── models.py         # Modelos de doação e badges
│   ├── views.py          # Views de doações
│   ├── serializers.py    # Serializers de doações
│   ├── urls.py           # Rotas de doações
│   └── tests.py          # Testes de doações
├── 📄 manage.py          # Script de gerenciamento Django
├── 📄 requirements.txt   # Dependências de produção
├── 📄 requirements-dev.txt  # Dependências de desenvolvimento
├── 📄 Dockerfile         # Configuração Docker
├── 📄 Docker-compose.yml # Orquestração de containers
├── 📄 openapi.yaml       # Especificação OpenAPI da API
├── 📄 pytest.ini         # Configuração do pytest
├── 📄 .coveragerc        # Configuração de cobertura de testes
└── 📄 .env.example       # Exemplo de variáveis de ambiente
```

---

## 🔧 Comandos Úteis

### Docker

#### Gerenciamento do Projeto
```bash
# Iniciar containers em segundo plano
docker compose up -d

# Ver logs em tempo real
docker compose logs -f backend

# Parar containers
docker compose stop

# Parar e remover containers
docker compose down

# Parar e remover containers + volumes (CUIDADO: apaga o banco)
docker compose down -v

# Reiniciar apenas o backend
docker compose restart backend
```

#### Banco de Dados
```bash
# Criar migrações
docker compose exec backend python manage.py makemigrations

# Aplicar migrações
docker compose exec backend python manage.py migrate

# Criar superusuário
docker compose exec backend python manage.py createsuperuser

# Acessar shell do Django
docker compose exec backend python manage.py shell

# Acessar banco de dados diretamente
docker compose exec db psql -U postgres -d doacoes_db
```

#### Testes e Qualidade
```bash
# Executar todos os testes
docker compose exec backend python manage.py test

# Testes com verbosidade
docker compose exec backend python manage.py test --verbosity=2

# Executar testes com pytest
docker compose exec backend pytest

# Cobertura de testes (Coverage.py)
docker compose exec backend coverage run --source='.' manage.py test
docker compose exec backend coverage report
docker compose exec backend coverage html
# Depois abra: htmlcov/index.html

# Testes com pytest e cobertura (gera relatório HTML)
docker compose exec backend pytest --cov=. --cov-report=term-missing --cov-report=html

# Relatório HTML completo com pytest-html
docker compose exec backend pytest --cov=. --cov-report=html --html=report.html --self-contained-html

# Verificar problemas no código
docker compose exec backend python manage.py check

# Formatar código (requer requirements-dev.txt)
docker compose exec backend black .

# Ordenar imports
docker compose exec backend isort .

# Verificar estilo
docker compose exec backend flake8

# Análise de segurança
docker compose exec backend bandit -r .
```

#### Documentação
```bash
# Gerar arquivo OpenAPI atualizado
docker compose exec backend python manage.py spectacular --color --file openapi.yaml
```

### Desenvolvimento Local

#### Banco de Dados
```bash
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Verificar status das migrações
python manage.py showmigrations

# Reverter migração
python manage.py migrate <app_name> <migration_name>
```

#### Testes
```bash
# Executar todos os testes
python manage.py test

# Executar testes de um app específico
python manage.py test contas

# Executar teste específico
python manage.py test contas.tests.ListarUsuariosTestCase.test_admin_lista_todos_usuarios

# Testes com verbosidade
python manage.py test --verbosity=2

# Manter banco de dados de teste após execução
python manage.py test --keepdb

# Executar testes com pytest
pytest

# Cobertura de testes
coverage run --source='.' manage.py test
coverage report           # Relatório no terminal
coverage report --show-missing  # Mostra linhas não cobertas
coverage html             # Gera relatório HTML em htmlcov/
```

#### Qualidade de Código
```bash
# Formatar código automaticamente
black .

# Verificar formatação sem aplicar
black --check .

# Ordenar imports
isort .

# Verificar código com flake8
flake8

# Análise de segurança com bandit
bandit -r .

# Verificar vulnerabilidades em dependências
safety check

# Verificar problemas no projeto
python manage.py check
```

#### Utilitários
```bash
# Abrir shell interativo do Django
python manage.py shell

# Abrir shell do banco de dados
python manage.py dbshell

# Coletar arquivos estáticos (produção)
python manage.py collectstatic

# Criar admin automaticamente (variáveis no .env)
python manage.py createsuperuser --noinput

# Gerar arquivo OpenAPI
python manage.py spectacular --color --file openapi.yaml

# Limpar sessões expiradas
python manage.py clearsessions
```

---

## 🧪 Testes

O projeto utiliza **banco de dados em memória (SQLite)** para testes, garantindo:
- ✅ **Testes rápidos** (10x mais rápido que PostgreSQL)
- ✅ **Isolamento total** entre testes
- ✅ **Não interfere** com banco de desenvolvimento
- ✅ **CI/CD otimizado** sem necessidade de serviços externos

### Estrutura de Testes

Cada app possui seus próprios testes organizados:
- `contas/tests.py` - Testes de autenticação, registro e gerenciamento de usuários
- `doacoes/tests.py` - Testes de criação, listagem e gerenciamento de doações

### Executando Testes

```bash
# Com Docker
docker compose exec backend python manage.py test

# Desenvolvimento local
python manage.py test

# Com pytest (mais verboso e com plugins)
pytest
```

### Cobertura de Código

**Meta:** **>80% de cobertura**

```bash
# Gerar cobertura
coverage run --source='.' manage.py test

# Ver relatório no terminal
coverage report

# Ver relatório detalhado com linhas não cobertas
coverage report --show-missing

# Gerar relatório HTML interativo
coverage html
# Abra htmlcov/index.html no navegador
```

### Boas Práticas de Testes

- ✅ Use `TestCase` do Django para testes que usam banco de dados
- ✅ Use `APITestCase` do DRF para testes de API
- ✅ Sempre teste casos de sucesso e falha
- ✅ Teste permissões e autenticação
- ✅ Use fixtures ou factories para dados de teste
- ✅ Mantenha testes isolados e independentes

---

## 🧩 Documentação da API

O projeto utiliza **drf-spectacular** para gerar a especificação OpenAPI 3.0 automaticamente a partir do código.

### URLs de Documentação

- **OpenAPI Schema (JSON)**: `http://localhost:8000/api/schema/`
- **Swagger UI** (Interativo): `http://localhost:8000/api/schema/swagger-ui/`
- **ReDoc** (Alternativo): `http://localhost:8000/api/schema/redoc/`

### Principais Endpoints

#### Autenticação
```
POST   /api/token/              # Obter token JWT
POST   /api/token/refresh/      # Renovar token
POST   /api/contas/cadastrar/   # Cadastrar novo usuário
```

#### Usuários
```
GET    /api/contas/usuarios/           # Listar usuários (admin)
GET    /api/contas/usuarios/{id}/      # Detalhes do usuário
PUT    /api/contas/usuarios/{id}/      # Atualizar usuário
DELETE /api/contas/usuarios/{id}/      # Deletar usuário
GET    /api/contas/perfil/             # Ver próprio perfil
```

#### Doações
```
GET    /api/doacoes/               # Listar doações
POST   /api/doacoes/               # Criar doação
GET    /api/doacoes/{id}/          # Detalhes da doação
PUT    /api/doacoes/{id}/          # Atualizar doação
DELETE /api/doacoes/{id}/          # Deletar doação
GET    /api/doacoes/minhas/        # Minhas doações
```

### Autenticação JWT

A API usa **JSON Web Tokens (JWT)** para autenticação:

#### 1. Obter Token
```bash
POST /api/token/
Content-Type: application/json

{
  "username": "seu_usuario",
  "password": "sua_senha"
}

# Resposta:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 2. Usar Token nas Requisições
```bash
GET /api/doacoes/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

#### 3. Renovar Token Expirado
```bash
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# Resposta:
{
  "access": "novo_token_access..."
}
```

### Exemplo de Requisição Completa

```bash
# 1. Obter token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "senha123"}'

# 2. Usar token para listar doações
curl -X GET http://localhost:8000/api/doacoes/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Testando a API

Use o **Swagger UI** (`/api/schema/swagger-ui/`) para testar todos os endpoints de forma interativa:
1. Clique em "Authorize" no topo
2. Cole seu token JWT no campo `Bearer <token>`
3. Teste os endpoints diretamente pela interface

---

## 🚀 Deploy

### Deploy no Render

O projeto está configurado para deploy no [Render](https://render.com/):

1. **Configure as variáveis de ambiente no Render:**
   - `DEBUG=False`
   - `SECRET_KEY=<chave-segura>`
   - `DATABASE_URL=<url-do-postgresql>`
   - `ALLOWED_HOSTS=seu-app.onrender.com`
   - Configure AWS S3 para armazenamento de mídia (opcional)

2. **O Render detectará automaticamente:**
   - `requirements.txt` para instalar dependências
   - Executará migrações automaticamente
   - Usará Gunicorn como servidor WSGI

3. **Arquivo openapi.yaml:**
   - Atualizado automaticamente pela API
   - Use para documentação externa ou integrações

### Deploy com Docker

```bash
# Build da imagem de produção
docker build -t ecodoacao-backend .

# Executar container
docker run -p 8000:8000 --env-file .env ecodoacao-backend
```

### Checklist de Produção

- [ ] `DEBUG=False` no .env
- [ ] `SECRET_KEY` forte e único
- [ ] `ALLOWED_HOSTS` configurado corretamente
- [ ] `CORS_ALLOWED_ORIGINS` apenas origens confiáveis
- [ ] Banco de dados PostgreSQL configurado
- [ ] Armazenamento de mídia configurado (S3/Cloudinary)
- [ ] Variáveis de ambiente protegidas
- [ ] HTTPS habilitado
- [ ] Backups do banco de dados automatizados

---

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. **Erro de conexão com banco de dados**
```bash
# Verifique se o PostgreSQL está rodando
docker compose ps

# Reinicie o banco de dados
docker compose restart db

# Verifique logs
docker compose logs db
```

#### 2. **Migrações não aplicadas**
```bash
# Verifique status das migrações
docker compose exec backend python manage.py showmigrations

# Force aplicação de migrações
docker compose exec backend python manage.py migrate --run-syncdb
```

#### 3. **Porta 8000 já em uso**
```bash
# Identifique o processo
lsof -i :8000

# Mate o processo (Linux/Mac)
kill -9 <PID>

# Ou altere a porta no docker-compose.yml
ports:
  - "8001:8000"  # host:container
```

#### 4. **Problemas com permissões (Linux)**
```bash
# Ajuste permissões do projeto
sudo chown -R $USER:$USER .

# Reconstrua os containers
docker compose down
docker compose up --build
```

#### 5. **Erro ao importar módulos**
```bash
# Reinstale dependências
pip install -r requirements.txt --force-reinstall

# Com Docker
docker compose exec backend pip install -r requirements.txt --force-reinstall
```

#### 6. **Token JWT inválido ou expirado**
- Obtenha um novo token em `/api/token/`
- Use o refresh token em `/api/token/refresh/`
- Verifique configurações de tempo em `settings.py`

#### 7. **Testes falhando**
```bash
# Limpe cache do Python
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Recrie banco de testes
python manage.py test --keepdb=False
```

### Logs e Debug

```bash
# Ver logs em tempo real
docker compose logs -f backend

# Ver apenas últimas 100 linhas
docker compose logs --tail=100 backend

# Modo debug no Django
# Ative DEBUG=True no .env (apenas desenvolvimento!)
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Siga estas etapas:

### 1. Fork e Clone

```bash
# Fork o repositório no GitHub
# Clone seu fork
git clone https://github.com/SEU-USUARIO/ecodoacao-backend.git
cd ecodoacao-backend
```

### 2. Configure o Ambiente

```bash
# Crie uma branch para sua feature
git checkout -b feature/minha-feature

# Instale dependências de desenvolvimento
pip install -r requirements-dev.txt
```

### 3. Faça suas Alterações

- Escreva código limpo e documentado
- Siga as convenções PEP 8
- Adicione testes para novas funcionalidades
- Mantenha cobertura de testes >80%

### 4. Teste suas Alterações

```bash
# Execute testes
python manage.py test

# Verifique cobertura
coverage run --source='.' manage.py test
coverage report

# Formate o código
black .
isort .

# Verifique estilo
flake8

# Análise de segurança
bandit -r .
```

### 5. Commit e Push

```bash
# Commit suas mudanças
git add .
git commit -m "feat: adiciona nova funcionalidade X"

# Push para seu fork
git push origin feature/minha-feature
```

### 6. Abra um Pull Request

- Descreva claramente suas mudanças
- Referencie issues relacionadas
- Aguarde revisão

### Convenções de Commit

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Alterações na documentação
- `style:` - Formatação, ponto e vírgula, etc
- `refactor:` - Refatoração de código
- `test:` - Adição ou correção de testes
- `chore:` - Tarefas de manutenção

### Código de Conduta

- Seja respeitoso e profissional
- Aceite críticas construtivas
- Foque no que é melhor para o projeto
- Ajude outros contribuidores

---

## 🛠️ Melhorias Futuras

- [x] Testes automatizados
- [x] Coverage reports
- [x] Documentação OpenAPI/Swagger
- [x] Sistema de badges
- [ ] CI/CD com GitHub Actions
- [ ] Cache com Redis
- [ ] Sistema de notificações
- [ ] Busca avançada com Elasticsearch
- [ ] Rate limiting
- [ ] Versionamento de API
- [ ] WebSockets para atualizações em tempo real

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

```
MIT License

Copyright (c) 2025 Ecodoação Universitaria

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 👥 Autores

**Ecodoação Universitaria**

- GitHub: [@Ecodoacao-Universitaria](https://github.com/Ecodoacao-Universitaria)

---

## 📞 Suporte

- 📧 Abra uma [issue](https://github.com/Ecodoacao-Universitaria/ecodoacao-backend/issues) para reportar bugs
- 💬 Use [discussions](https://github.com/Ecodoacao-Universitaria/ecodoacao-backend/discussions) para perguntas
- ⭐ Deixe uma estrela se este projeto foi útil!

---

<div align="center">
  <strong>Desenvolvido com ❤️ pela comunidade Ecodoação</strong>
</div>