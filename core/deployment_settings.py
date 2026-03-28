import os
import dj_database_url
from .settings import *  # noqa
from .settings import BASE_DIR  # noqa

# ============================================================
# PRODUCTION SETTINGS — RENDER
# ============================================================

DEBUG = False

# ------------------------------------------------------------
# SECRET KEY
# ------------------------------------------------------------

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY manquant dans les variables d'environnement")

# ------------------------------------------------------------
# HOSTS / DOMAINS
# ------------------------------------------------------------

RENDER_HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
FRONTEND_URL = os.environ.get("FRONTEND_URL")  # ex: https://jo-etickets-frontend.onrender.com

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]

if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)

# ------------------------------------------------------------
# CSRF
# ------------------------------------------------------------

CSRF_TRUSTED_ORIGINS = []

if RENDER_HOST:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_HOST}")

if FRONTEND_URL:
    CSRF_TRUSTED_ORIGINS.append(FRONTEND_URL)

# ------------------------------------------------------------
# CORS
# ------------------------------------------------------------

CORS_ALLOWED_ORIGINS = []

if FRONTEND_URL:
    CORS_ALLOWED_ORIGINS.append(FRONTEND_URL)

CORS_ALLOW_CREDENTIALS = True

# ------------------------------------------------------------
# MIDDLEWARE
# ------------------------------------------------------------

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ------------------------------------------------------------
# STATIC FILES
# ------------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True,
    )
}

# ------------------------------------------------------------
# SECURITY
# ------------------------------------------------------------

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# ------------------------------------------------------------
# LOGGING
# ------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}