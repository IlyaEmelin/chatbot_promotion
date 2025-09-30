import logging
from os import getenv, path
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

ALLOWED_HOSTS = ["*"]

BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": (
                "{levelname} {asctime} "
                "{module} {class_name}.{method_name} "
                "{process:d} {thread:d} {message}"
            ),
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "filters": {
        "add_class_method": {
            "()": "chatbot_promotion.logging_filters.ClassMethodFilter",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "filters": ["add_class_method"],
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": path.join(BASE_DIR / "logs", "django.log"),
            "formatter": "verbose",
            "filters": ["add_class_method"],
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": getenv("LOGGING_LEVEL", "INFO"),
            "propagate": False,
        },
        "api": {
            "handlers": ["console", "file"],
            "level": getenv("LOGGING_LEVEL", "INFO"),
            "propagate": False,
        },
        "recipes": {
            "handlers": ["console", "file"],
            "level": getenv("LOGGING_LEVEL", "INFO"),
            "propagate": False,
        },
        "users": {
            "handlers": ["console", "file"],
            "level": getenv("LOGGING_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}
logger = logging.getLogger(__name__)

SECRET_KEY = getenv("SECRET_KEY", default=get_random_secret_key())

DEBUG = getenv("DEBUG", "").lower() == "true"
# Ya disk token
DISK_TOKEN = getenv("DISK_TOKEN", "")

AUTH_USER_MODEL = "users.User"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",
    "drf_yasg",
    "questionnaire",
    "api",
    "telegram_bot",
    "users",
]

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

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = "chatbot_promotion.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "chatbot_promotion.wsgi.application"

SWAGGER_USE_COMPAT_RENDERERS = False

if getenv("ENABLE_POSTGRES_DB", "").lower() == "true":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": getenv("POSTGRES_DB"),
            "USER": getenv("POSTGRES_USER"),
            "PASSWORD": getenv("POSTGRES_PASSWORD"),
            "HOST": getenv("DB_HOST"),
            "PORT": 5432,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.NumericPasswordValidator"
        ),
    },
]

LANGUAGE_CODE = "ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "backend_static"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

TELEGRAM_BOT_TOKEN = getenv(
    "TELEGRAM_BOT_TOKEN",
    "your_bot_token_here",
)
TELEGRAM_WEBHOOK_URL = getenv(
    "TELEGRAM_WEBHOOK_URL",
    "https://yourdomain.com/webhook/",
)
TELEGRAM_ADMIN_IDS = getenv("ADMIN_IDS", "").split(",")

DISK_TOKEN = getenv("DISK_TOKEN", "dummy-key-for-dev")

CSRF_TRUSTED_ORIGINS = getenv("CSRF_TRUSTED", "http://localhost").split(",")
