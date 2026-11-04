"""
Django settings for campus_hub (Part 11: secured).

Secrets and deployment values come from environment variables, never from the code.
See ../.env.example for the full list.
"""

import os
import sys
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default):
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


# --- Core security settings, read from the environment ---
DEBUG = env_bool("DJANGO_DEBUG", True)  # development default; production sets DJANGO_DEBUG=0

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured("Set DJANGO_SECRET_KEY: production must not start without a real secret key.")
    SECRET_KEY = "django-insecure-development-only-key"  # never used when DEBUG is off

ALLOWED_HOSTS = [host.strip() for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if host.strip()]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'rooms',
    'bookings',
    'holiday_api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'campus_hub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'campus_hub.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation: weak passwords are rejected. Passwords are stored as salted PBKDF2 hashes by default.

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'


# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True


# Static files

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']


# Email: the console in development, a real SMTP server in production (settings from the environment)

if DEBUG:
    MAILERS = {'default': {'BACKEND': 'django.core.mail.backends.console.EmailBackend'}}
else:
    MAILERS = {
        'default': {
            'BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
            'OPTIONS': {
                'host': os.environ.get('EMAIL_HOST', 'localhost'),
                'port': int(os.environ.get('EMAIL_PORT', '587')),
                'username': os.environ.get('EMAIL_HOST_USER', ''),
                'password': os.environ.get('EMAIL_HOST_PASSWORD', ''),
                'use_tls': True,
                'timeout': 10,
            },
        },
    }
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'bookings@campus.example')


# Holidays API and notifications (Part 9)

TESTING = 'test' in sys.argv  # tests never call the real network by default
HOLIDAYS_ENABLED = not TESTING and env_bool('HOLIDAYS_ENABLED', True)
HOLIDAY_COUNTRY = 'PH'


# Tests only: a fast hasher keeps the suite quick. Real runs use Django's default (PBKDF2, deliberately slow).
if TESTING:
    PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']


# Production hardening: switched on whenever DEBUG is off (see docs/SECURITY.md)

if not DEBUG:
    SECURE_SSL_REDIRECT = True                 # send every request to HTTPS
    SESSION_COOKIE_SECURE = True               # the session cookie only travels over HTTPS
    CSRF_COOKIE_SECURE = True                  # the CSRF cookie only travels over HTTPS
    SECURE_HSTS_SECONDS = 31536000             # tell browsers to use HTTPS for a year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # only behind a proxy you control
