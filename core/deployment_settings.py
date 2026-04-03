# core/deployment_settings.py
from pathlib import Path
from decouple import config
import dj_database_url
from corsheaders.defaults import default_headers

# ============================================================
# BASE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = False

ALLOWED_HOSTS = [
    "jo-etickets-backend.onrender.com",
    "localhost",
    "127.0.0.1",
]

# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third‑party
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",

    # Local apps
    "users.apps.UsersConfig",
    "evenements",
    "offres",
    "paniers",
    "commandes",
    "billets",
    "paiements.apps.PaiementsConfig",
    "analytics.apps.AnalyticsConfig",
]

# ============================================================
# TEMPLATES (OBLIGATOIRE POUR DJANGO ADMIN)
# ============================================================

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

# ============================================================
# MIDDLEWARE (ORDRE CRUCIAL ✅)
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # ✅ WHITENOISE : OBLIGATOIRE POUR LES STATICS EN PROD
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ============================================================
# CORS / CSRF (PRODUCTION RENDER)
# ============================================================

CORS_ALLOWED_ORIGINS = [
    "https://jo-etickets-frontend.onrender.com",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
    "content-type",
]

CSRF_TRUSTED_ORIGINS = [
    "https://jo-etickets-frontend.onrender.com",
]

# ============================================================
# URLS / ASGI / WSGI
# ============================================================

ROOT_URLCONF = "core.urls"

ASGI_APPLICATION = "core.asgi.application"
WSGI_APPLICATION = "core.wsgi.application"

# ============================================================
# DATABASE (RENDER)
# ============================================================

DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True,
    )
}

# ============================================================
# AUTH
# ============================================================

AUTH_USER_MODEL = "users.Utilisateur"

# ============================================================
# REST FRAMEWORK
# ============================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

# ============================================================
# INTERNATIONALISATION
# ============================================================

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

# ============================================================
# STATIC FILES ✅ (FIX CRITIQUE)
# ============================================================

STATIC_URL = "/static/"

# ✅ Dossier où collectstatic copie TOUT
STATIC_ROOT = BASE_DIR / "staticfiles"

# ✅ Optionnel mais safe
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# ✅ STORAGE WHITENOISE (OBLIGATOIRE)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ============================================================
# SECURITY (RENDER / HTTPS)
# ============================================================

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

X_FRAME_OPTIONS = "DENY"

# ============================================================
# LOGGING (RENDER)
# ============================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}