import os
from pathlib import Path

import environ

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
)
environ.Env.read_env(os.path.join(BASE_DIR.parent, ".env"))  # looks for ../.env relative to settings.py

# SECURITY WARNING: keep the secret key used in production!
SECRET_KEY = env("DJANGO_SECRET_KEY", default="unsafe-dev-key")

# SECURITY WARNING: turn this off in production!
DEBUG = env("DJANGO_DEBUG", default=True)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*", "*.ngrok-free.app", "*.ngrok.io", "localhost", "127.0.0.1"])

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Your custom app
    "apps.agent_core",
    "apps.chat_assistant",
    "apps.dashboard",
    # 3rd-party
    "rest_framework",
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # CORS before CommonMiddleware
    "apps.agent_core.middleware.NgrokHostMiddleware",  # Custom ngrok host middleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # Add locale middleware
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",  # Add i18n context processor
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
if env("DATABASE_URL", default=None):
    import dj_database_url

    DATABASES = {"default": dj_database_url.parse(env("DATABASE_URL"))}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Static files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # For collectstatic in production

# REST Framework configuration
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
}

# CORS configuration (adjust as needed)
CORS_ALLOW_ALL_ORIGINS = True  # 🔐 For dev only. Set to False and use CORS_ALLOWED_ORIGINS in production

# Default primary key field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Internationalization
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Language settings
LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English"),
    ("es", "Español"),
]

# Locale paths
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# Time zone
TIME_ZONE = "UTC"