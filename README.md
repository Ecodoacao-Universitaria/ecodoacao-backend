# 🌱 EcoDoação - Backend

API em Django REST Framework para gerenciamento de contas e doações.

## 🚀 Tecnologias

- **Python 3.11**
- **Django 5**
- **Django REST Framework**
- **PostgreSQL**
- **Docker & Docker Compose**
- **drf-spectacular** (documentação OpenAPI/Swagger)
- **Coverage.py** (cobertura de testes)

---

## 🧰 Pré-requisitos

- Docker e Docker Compose instalados  
- Arquivo `.env` configurado com suas variáveis (copie do `.env.example`)
```bash
# Copie o arquivo de exemplo e edite com suas configurações
cp .env.example .env
```

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

# 3. Suba os containers
docker compose up --build

# 4. Acesse a API
# http://localhost:8000/api/

# 5. Documentação Swagger
# http://localhost:8000/api/docs/
```

### Desenvolvimento Local (Sem Docker)
```bash
# 1. Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 2. Instale as dependências
pip install -r requirements.txt
# Para desenvolvimento (inclui ferramentas de teste e qualidade)
pip install -r requirements-dev.txt

# 3. Configure o .env
cp .env.example .env

# 4. Execute as migrações
python manage.py migrate

# 5. Crie um superusuário
python manage.py createsuperuser

# 6. Execute o servidor
python manage.py runserver
```

---

## 📁 Estrutura do Projeto
```
core/              # Configurações principais do Django
contas/            # App de autenticação e usuários
doacoes/           # App principal de doações
.coveragerc        # Configuração de cobertura de testes
Dockerfile
docker-compose.yml
requirements.txt
requirements-dev.txt
.env.example
```

---

## 🔧 Comandos Úteis

### Docker
```bash
# Rodar migrações
docker compose exec backend python manage.py migrate

# Criar superusuário
docker compose exec backend python manage.py createsuperuser

# Ver logs do backend
docker compose logs backend -f

# Executar testes
docker compose exec backend python manage.py test

# Executar testes com cobertura
docker compose exec backend coverage run --source='.' manage.py test
docker compose exec backend coverage report
docker compose exec backend coverage html

# Acessar relatório HTML de cobertura
# Abra: htmlcov/index.html no navegador após rodar 'coverage html'

# Parar containers
docker compose down

# Parar e remover volumes
docker compose down -v
```

### Desenvolvimento Local
```bash
# Executar testes
python manage.py test

# Executar testes de um app específico
python manage.py test contas

# Executar um teste específico
python manage.py test contas.tests.ListarUsuariosTestCase.test_admin_lista_todos_usuarios

# Testes com verbosidade (mostra cada teste rodando)
python manage.py test --verbosity=2

# Cobertura de testes
coverage run --source='.' manage.py test
coverage report  # Relatório no terminal
coverage html    # Gera relatório HTML em htmlcov/

# Criar novas migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Verificar problemas
python manage.py check

# Com requirements-dev.txt instalado:
# Formatar código
black .

# Ordenar imports
isort .

# Verificar estilo
flake8

# Análise de segurança
bandit -r .
```

---

## 🧪 Testes

O projeto utiliza **banco de dados em memória** para testes, garantindo:
- ✅ Testes rápidos (10x mais rápido que PostgreSQL)
- ✅ Isolamento total entre testes
- ✅ Não interfere com banco de desenvolvimento

### Estrutura de Testes

Cada app possui seus próprios testes:
- `contas/tests.py` - Testes de autenticação e gerenciamento de usuários
- `doacoes/tests.py` - Testes de doações e campanhas

### Cobertura de Código

Meta: **>80% de cobertura**
```bash
# Ver relatório detalhado
coverage report --show-missing

# Ver quais linhas não estão cobertas
coverage html
# Abra htmlcov/index.html no navegador
```

---

## 🧩 Documentação da API

O projeto utiliza **drf-spectacular**, gerando a especificação OpenAPI automaticamente.

- **Schema JSON**: `/api/schema/`
- **Swagger UI**: `/api/schema/swagger-ui/`
- **ReDoc**: `/api/schema/redoc/`

### Autenticação

A API usa **JWT (JSON Web Tokens)** para autenticação:

1. Obter token: `POST /api/token/`
```json
{
  "username": "seu_usuario",
  "password": "sua_senha"
}
```

2. Usar token nas requisições:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

3. Renovar token: `POST /api/token/refresh/`

---

## 🛠️ Melhorias Futuras

- [x] Testes automatizados
- [x] Coverage reports

---

## 📄 Licença