from pathlib import Path
from dotenv import load_dotenv
import os, sys
import dj_database_url
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')
SECRET_KEY = os.getenv('SECRET_KEY') or 'unsafe-dev-key'

if not SECRET_KEY:
    if DEBUG:
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

ALLOWED_HOSTS_STRING = os.getenv('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = ALLOWED_HOSTS_STRING.split(',') if ALLOWED_HOSTS_STRING else []

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
    'drf_spectacular',
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

# Database: usa DATABASE_URL em produção, DB_* em dev
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    DB_ENGINE = os.getenv('DB_ENGINE', 'django.db.backends.sqlite3')
    if 'postgresql' in DB_ENGINE:
        DATABASES = {
            'default': {
                'ENGINE': DB_ENGINE,
                'NAME': os.getenv('DB_NAME', 'doacoes_db'),
                'USER': os.getenv('DB_USER', 'postgres'),
                'PASSWORD': os.getenv('DB_PASSWORD', ''),
                'HOST': os.getenv('DB_HOST', 'localhost'),
                'PORT': os.getenv('DB_PORT', '5432'),
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

if 'test' in sys.argv or 'test_coverage' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
    MIGRATION_MODULES = {
        'contas': None,
        'doacoes': None,
        'admin': None,
        'auth': None,
        'contenttypes': None,
        'sessions': None,
    }

AUTH_USER_MODEL = 'contas.Usuario'

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "core.validators.MinSixAlphaNumericValidator"},
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Recife'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS_STRING = os.getenv('CORS_ALLOWED_ORIGINS', '')
CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS_STRING.split(',') if CORS_ALLOWED_ORIGINS_STRING else []
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    # corrige duplicidade e aponta para o arquivo certo
    'EXCEPTION_HANDLER': 'core.exceptions.drf_exception_handler',
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

if not DEBUG:
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'sa-east-1')
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = 'public-read'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

if DEBUG:
    import socket
    INTERNAL_IPS = ['127.0.0.1', 'localhost']
    try:
        hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
        INTERNAL_IPS += [ip[: ip.rfind(".")] + ".1" for ip in ips]
    except:
        pass
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    }