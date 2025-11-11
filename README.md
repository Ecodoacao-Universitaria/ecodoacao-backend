# 🌱 EcoDoação - Backend

API em Django REST Framework para gerenciamento de contas e doações.

## 🚀 Tecnologias

- **Python 3.11**
- **Django 5**
- **Django REST Framework**
- **PostgreSQL**
- **Docker & Docker Compose**
- **drf-spectacular** (documentação OpenAPI/Swagger)

---

## 🧰 Pré-requisitos

- Docker e Docker Compose instalados  
- Arquivo `.env` configurado com suas variáveis (exemplo abaixo)

```env
DEBUG=1
SECRET_KEY=changeme
POSTGRES_DB=doacoes_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_HOST=db
POSTGRES_PORT=5432


# 1. Suba os containers
docker compose up --build

# 2. Acesse a API
http://localhost:8000/api/

# 3. Documentação Swagger
http://localhost:8000/api/schema/swagger-ui/


core/              # Configurações principais do Django
contas/            # App de autenticação e usuários
doacoes/           # App principal de doações
Dockerfile
docker-compose.yml
requirements.txt


# Rodar migrações
docker compose exec backend python manage.py migrate

# Criar superusuário
docker compose exec backend python manage.py createsuperuser

# Ver logs do backend
docker logs doacoes_backend -f


🧩 Documentação da API

O projeto utiliza drf-spectacular, gerando a especificação OpenAPI automaticamente.

Schema JSON: /api/schema/

Swagger UI: /api/schema/swagger-ui/

ReDoc: /api/schema/redoc/


🛠️ Melhorias Futuras

Testes automatizados (pytest + coverage)

CI/CD (GitHub Actions)

Cache e fila (Redis + Celery)