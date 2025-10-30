import logging
from os import getenv, path
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

ALLOWED_HOSTS = ["*"]

BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING_OUTPUT = getenv("LOGGING_DESTINATION", "console file").split(" ")
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
            "level": getenv("LOGGING_LEVEL", "INFO"),
            "class": "logging.FileHandler",
            "filename": path.join(BASE_DIR / "logs", "django.log"),
            "formatter": "verbose",
            "filters": ["add_class_method"],
        },
    },
    "root": {
        "handlers": LOGGING_OUTPUT,
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": LOGGING_OUTPUT,
            "level": getenv("LOGGING_LEVEL", "INFO"),
            "propagate": False,
        },
        "api": {
            "handlers": LOGGING_OUTPUT,
            "level": getenv("LOGGING_LEVEL", "INFO"),
            "propagate": False,
        },
        "telegram_bot": {
            "handlers": LOGGING_OUTPUT,
            "level": getenv("LOGGING_LEVEL", "INFO"),
            "propagate": False,
        },
        "users": {
            "handlers": LOGGING_OUTPUT,
            "level": getenv("LOGGING_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}
logger = logging.getLogger(__name__)

SECRET_KEY = getenv("SECRET_KEY", default=get_random_secret_key())

DEBUG = getenv("DEBUG", "").lower() == "true"
CSRF_TRUSTED_ORIGINS = getenv("CSRF_TRUSTED", "http://localhost").split(",")

AUTH_USER_MODEL = "users.User"

INSTALLED_APPS = [
    "unfold",
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
    "django.middleware.locale.LocaleMiddleware",
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


# SWAGGER_USE_COMPAT_RENDERERS = False

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    },
    "USE_SESSION_AUTH": False,
    "JSON_EDITOR": True,
    "OPERATIONS_SORTER": "alpha",
    "TAGS_SORTER": "alpha",
    "DOC_EXPANSION": "none",
    "DEEP_LINKING": True,
}

# Дополнительно для Redoc
REDOC_SETTINGS = {
    "SPEC_URL": ("schema-json", {"format": ".json"}),
}


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
    "DEFAULT_THROTTLE_RATES": {
        "user": "10000/day",
        "anon": "1000/day",
    },
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

UNFOLD = {
    "SITE_TITLE": "ПРО-ДВИЖЕНИЕ",
    "SITE_HEADER": "ПРО-ДВИЖЕНИЕ",
    "SITE_ICON": "staticfiles/admin_logo.svg"
}

LANGUAGE_CODE = "ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "backend_static"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Ya disk token
DISK_TOKEN = getenv("DISK_TOKEN", "")

TELEGRAM_BOT_TOKEN = getenv(
    "TELEGRAM_BOT_TOKEN",
    "your_bot_token_here",
)
TELEGRAM_WEBHOOK_URL = getenv(
    "TELEGRAM_WEBHOOK_URL",
    "https://yourdomain.com/webhook/",
)
TELEGRAM_ADMIN_IDS = getenv("ADMIN_IDS", "").split(",")
# Отображать в текстовом сообщение вариант ответа на русском
TELEGRAM_SHOW_RESPONSE_CHOICE = (
    getenv(
        "TELEGRAM_SHOW_RESPONSE_CHOICE",
        "false",
    ).lower()
    == "true"
)
# Отображать в телеграмм боте ответ "Вернуться к предыдущему вопросу"
TELEGRAM_SHOW_REVERT_PREVIOUS_QUESTION = (
    getenv("TELEGRAM_SHOW_REVERT_PREVIOUS_QUESTION", "false").lower() == "true"
)

DEFAULT_DISK_TOKEN = "dummy-key-for-dev"
DISK_TOKEN = getenv("DISK_TOKEN", DEFAULT_DISK_TOKEN)
