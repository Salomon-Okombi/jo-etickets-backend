from pathlib import Path
from decouple import config, Csv
from datetime import timedelta

# =========================================================
# BASE
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# SÉCURITÉ
# =========================================================
SECRET_KEY = config("SECRET_KEY", default="dev-secret-key-change-me")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())


# =========================================================
# APPLICATIONS
# =========================================================
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "django_filters",

    # Third-party
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_yasg",
    "channels",

    # Apps métier
    "users",
    "evenements",
    "offres",
    "paniers",
    "paiements",
    "billets",
    "analytics",
    "notifications",
    "commandes",
]


# =========================================================
# MIDDLEWARE (ORDRE CRITIQUE)
# =========================================================
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =========================================================
# URLS / WSGI / ASGI
# =========================================================
ROOT_URLCONF = "core.urls"

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"


# =========================================================
# CHANNELS (DEV)
# =========================================================
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}


# =========================================================
# TEMPLATES
# =========================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# =========================================================
# BASE DE DONNÉES (MySQL)
# =========================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="127.0.0.1"),
        "PORT": config("DB_PORT", default=3306, cast=int),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "charset": "utf8mb4",
        },
    }
}



# =========================================================
# UTILISATEUR PERSONNALISÉ
# =========================================================
AUTH_USER_MODEL = "users.Utilisateur"


# =========================================================
# AUTHENTIFICATION & HASHING
# =========================================================
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]


# =========================================================
# DJANGO REST FRAMEWORK + JWT
# =========================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,

    
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],

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


# =========================================================
# INTERNATIONALISATION
# =========================================================
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True


# =========================================================
# FICHIERS STATIQUES & MÉDIAS
# =========================================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
APPEND_SLASH = True


# =========================================================
# CORS (FRONTEND)
# =========================================================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
CORS_ALLOW_CREDENTIALS = True


# =========================================================
# EMAIL (RESET MOT DE PASSE)
# =========================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_PASSWORD", default="")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# =========================================================
# LOGGING
# =========================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs/django.log",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}


# =========================================================
# SÉCURITÉ PROD
# =========================================================
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = "DENY"
