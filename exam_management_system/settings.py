"""
exam_management_system.settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Central configuration module for the Django exam_management_system project.

This file defines:
- Core security and environment-based settings
- Installed Django applications and middleware stack
- URL and WSGI configuration
- Database selection and connection settings
- Internationalization and timezone configuration
- Static files handling
- Cache configuration
- Email backend settings
- Authentication redirects
- Logging configuration
- Custom user model placeholder
"""

# ============================
# Imports
# ============================
from pathlib import Path
import os
import sys
import dotenv


# ============================
# Load environment variables
# ============================
# Loads variables from a .env file into the environment
dotenv.load_dotenv()


# ============================
# Base directory
# ============================
# BASE_DIR points to the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent


# ============================
# Security & Environment
# ============================

# SECRET_KEY
# Must be provided through environment variables.
# The app will refuse to start if it's missing.
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not set")

# DEBUG
# Enabled only when DEBUG=True explicitly in environment variables
DEBUG = os.getenv("DEBUG") == "True"

# TESTING
# Detects Django test runs (manage.py test)
TESTING = "test" in sys.argv

# ENVIRONMENT
# Defines deployment environment: production / staging / development
ENVIRONMENT = os.getenv("ENV", "production").lower()


# ============================
# Allowed hosts
# ============================
# Hosts allowed to serve the application (comma-separated)
ALLOWED_HOSTS = [host for host in os.getenv("ALLOWED_HOSTS", "").split(",") if host]


# ============================
# Application definition
# ============================
INSTALLED_APPS = [
    "exams",  # Main exams app
    "accounts",  # Custom user accounts app
    "errors",  # Custom error handling app for bad requests, permission issues, and not found errors
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]


# ============================
# Middleware
# ============================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Static file handling in production
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================
# URL & WSGI configuration
# ============================
ROOT_URLCONF = "exam_management_system.urls"
WSGI_APPLICATION = "exam_management_system.wsgi.application"


# ============================
# Production security settings
# ============================
# These settings are applied only when:
# - Environment is production
# - DEBUG is False
# - Not running tests
if ENVIRONMENT == "production" and not DEBUG and not TESTING:
    CSRF_TRUSTED_ORIGINS = [
        origin for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if origin
    ]
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # Enforce HTTPS for 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True
    SESSION_SAVE_EVERY_REQUEST = True
    X_FRAME_OPTIONS = "DENY"


# ============================
# Database configuration
# ============================
# Select database engine via environment variable
DB_ENGINE = os.getenv("DB_ENGINE", "sqlite")

if DB_ENGINE == "mysql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ["DB_NAME"],
            "USER": os.environ["DB_USER"],
            "PASSWORD": os.environ["DB_PASSWORD"],
            "HOST": os.environ["DB_HOST"],
            "PORT": os.getenv("DB_PORT", "4000"),
            "OPTIONS": {
                # SSL configuration for secure MySQL connections
                "ssl": {
                    "ca": BASE_DIR / "certs" / "ca.pem",
                },
                "ssl_mode": "VERIFY_IDENTITY",
            },
        }
    }
else:
    # SQLite database for local development or fallback
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "_data" / "db.sqlite3",
        }
    }


# ============================
# Password validation
# ============================
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ============================
# Templates
# ============================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # Can be extended with custom template directories
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ============================
# Internationalization
# ============================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True


# ============================
# Static files
# ============================
# Directory where collectstatic stores files
STATIC_ROOT = BASE_DIR / "staticfiles"

# URL prefix for static files
STATIC_URL = "/static/"

# WhiteNoise storage with compression and cache-busting
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ============================
# Media files
# ============================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ============================
# Default primary key type
# ============================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================
# Cache settings
# ============================
# Caches configuration (using local memory cache for simplicity)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}


# ============================
# Email settings
# ============================
# Email backend configuration (console backend for development)
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")


# ============================
# Authentication redirects
# ============================
LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/auth/login/"


# ============================
# Logging
# ============================
# Simple console logging for visibility in production and development
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}


# ============================
# User model
# ============================
# Custom user model can be defined here if needed
AUTH_USER_MODEL = "accounts.User"
