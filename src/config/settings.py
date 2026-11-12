"""Atendimento local com conexão ao navegador e login manual nos sistemas externos."""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=False)
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if len(SECRET_KEY) < 50:
    raise ImproperlyConfigured("Gere a chave local executando scripts/preparar.ps1.")

DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"
APP_MODE = os.environ.get("APP_MODE", "navegador")
if APP_MODE not in {"preparacao", "simulacao", "navegador"}:
    raise ImproperlyConfigured("Use APP_MODE=preparacao, simulacao ou navegador.")
NAVEGADOR_CDP = os.environ.get("NAVEGADOR_CDP") or "http://127.0.0.1:9222"
WHATSAPP_CAMPO_MENSAGEM = os.environ.get("WHATSAPP_CAMPO_MENSAGEM", "")
DATA_UPLOAD_MAX_MEMORY_SIZE = 16384

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "[::1]"]
INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "apps.atendimento",
    "apps.catalogo",
    "apps.siat",
    "apps.whatsapp",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "config.middleware.LocalOnlyMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "src" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ]
        },
    }
]
WSGI_APPLICATION = "config.wsgi.application"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / ".local" / "db.sqlite3",
    }
}
CSRF_COOKIE_SAMESITE = "Strict"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Fortaleza"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "src" / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Nao enviar relatorios de excecao por e-mail nem gravar logs de requisicoes em arquivos.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"null": {"class": "logging.NullHandler"}},
    "loggers": {"django.request": {"handlers": ["null"], "propagate": False}},
}
