
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
import os
import sys

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# AVISO DE SEGURANÇA: não execute com debug ativado em produção!
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

# AVISO DE SEGURANÇA: mantenha a chave secreta usada em produção em segredo!
SECRET_KEY = os.getenv('SECRET_KEY')

if not SECRET_KEY:
    if DEBUG:
        # Chave fixa para desenvolvimento - mantém sessões funcionando entre reinicializações
        SECRET_KEY = 'django-insecure-chave-dev-local-mude-isso-em-producao-' + 'k' * 20
        print("⚠️  AVISO: Usando SECRET_KEY padrão de desenvolvimento")
        print("    Para produção, defina SECRET_KEY nas variáveis de ambiente")
        print("    Gere uma com: python manage.py shell -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\"")
    else:
        raise ValueError(
            "SECRET_KEY deve ser definida em modo de produção!\n"
            "Gere uma com:\n"
            "  python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
        )


# Lê os hosts permitidos da variável de ambiente
ALLOWED_HOSTS_STRING = os.getenv('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = ALLOWED_HOSTS_STRING.split(',') if ALLOWED_HOSTS_STRING else []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'contas',
    'doacoes',
    'storages',
    "drf_spectacular",
]

if DEBUG and 'test' not in sys.argv:
    INSTALLED_APPS += ['debug_toolbar']


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG and 'test' not in sys.argv:
    MIDDLEWARE.insert(1, 'debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases


DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Estamos no Render (Produção)
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,      # Mantém conexões abertas
            ssl_require=True       # Render exige conexão SSL
        )
    }
else:
    # Estamos localmente (Desenvolvimento)
    # Usa as variáveis do seu arquivo .env
    DATABASES = {
        'default': {    
            'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }

if 'test' in sys.argv or 'test_coverage' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',  # Banco em memória (super rápido)
        }
    }
    
    # Desabilita migrações nos testes (usa o schema direto do model)
    MIGRATION_MODULES = {
        'contas': None,
        'doacoes': None,
        'admin': None,
        'auth': None,
        'contenttypes': None,
        'sessions': None,
    }

# usuário personalizado
AUTH_USER_MODEL = 'contas.Usuario'

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'pt-br'  # Para português do Brasil

TIME_ZONE = 'America/Sao_Paulo'  # Fuso horário do Brasil

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
# permitir todas as origens para desenvolvimento
#CORS_ALLOW_ALL_ORIGINS = True


CORS_ALLOWED_ORIGINS_STRING = os.getenv('CORS_ALLOWED_ORIGINS', '')
CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS_STRING.split(',') if CORS_ALLOWED_ORIGINS_STRING else []
# permitir credenciais (cookies, autenticação HTTP, etc.)
CORS_ALLOW_CREDENTIALS = True


# Configurações do REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'EcoDoação API',
    'DESCRIPTION': 'API para gerenciamento de contas e doações',
    'VERSION': '1.0.0',
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    'SERVERS': [
        {'url': 'http://localhost:8000', 'description': 'Desenvolvimento'},
    ],
    
    'COMPONENT_SPLIT_REQUEST': True,
}

# Lógica para diferenciar desenvolvimento de produção
# No Render, é necessario configurar DEBUG como 'False'
if not DEBUG:
    # --- Configurações do Amazon S3 ---
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    
   
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'sa-east-1')  
    
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = 'public-read'
    
    # Diz ao Django para usar o S3 para todos os uploads de mídia
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
else:
    # --- Configurações para Desenvolvimento ---
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'


if DEBUG:
    import socket
    
    # IPs permitidos para acessar o debug toolbar
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
    
    # Para Docker: adiciona o IP do host
    try:
        hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
        INTERNAL_IPS += [ip[: ip.rfind(".")] + ".1" for ip in ips]
    except:
        pass
    
    # Configurações do Debug Toolbar
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    }