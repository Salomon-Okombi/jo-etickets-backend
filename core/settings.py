from pathlib import Path
import os
from decouple import config, Csv
from datetime import timedelta

# ---------------------
# Base
# ---------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------
# Sécurité
# ---------------------
SECRET_KEY = config("SECRET_KEY", default="changeme-en-prod")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())

# ---------------------
# Applications
# ---------------------
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # DRF + JWT
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_yasg',  
    # Applications internes
    'users',
    'billets',
    'offres',
    'evenements',
    'paniers',
    'paiements',
    'analytics',
]

# ---------------------
# Middleware
# ---------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Ajout optionnel : redirige HTTP → HTTPS si activé
    'django.middleware.security.SecurityMiddleware',
]

# ---------------------
# URLs / WSGI
# ---------------------
ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ---------------------
# Base de données MySQL
# ---------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config("DB_NAME"),
        'USER': config("DB_USER"),
        'PASSWORD': config("DB_PASSWORD", default=""),
        'HOST': config("DB_HOST", default="127.0.0.1"),
        'PORT': config("DB_PORT", default=3306, cast=int),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# ---------------------
# Utilisateur personnalisé
# ---------------------
AUTH_USER_MODEL = 'users.Utilisateur'

# ---------------------
# Authentification & Sécurité
# ---------------------
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# ---------------------
# Django REST Framework + JWT
# ---------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'STRICT_SLASHES': False,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        seconds=config("JWT_ACCESS_LIFETIME", default=3600, cast=int)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        seconds=config("JWT_REFRESH_LIFETIME", default=604800, cast=int)
    ),
    "SIGNING_KEY": config("JWT_SECRET", default=SECRET_KEY),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ---------------------
# Internationalisation
# ---------------------
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'  # plus cohérent avec un projet français
USE_I18N = True
USE_TZ = True

# ---------------------
# Fichiers statiques et médias
# ---------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
APPEND_SLASH = True

# ---------------------
# Sécurité renforcée en production
# ---------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

# ---------------------
# Email backend (utile pour reset mot de passe)
# ---------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_PASSWORD", default="")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ---------------------
# Logging (utile pour la prod)
# ---------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/django.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
