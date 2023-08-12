import datetime
from pathlib import Path

import environ

env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str(
    "SECRET_KEY", "django-insecure-34oqj72*yq6cky9nrubxyaw1^hvyybp&7=+uw%f-6wac%og4pn"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", str, ["*"])


DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_extensions",
    "django_filters",
    "drf_spectacular",
]

KAPIBARA_APPS = [
    "users",
    "posts",
    "communities",
]

INSTALLED_APPS = [
    *DJANGO_APPS,
    *THIRD_PARTY_APPS,
    *KAPIBARA_APPS,
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if env.bool("ENABLE_DB_STATS", default=False):
    MIDDLEWARE += ["common.middlewares.DBStatsMiddleware"]

ROOT_URLCONF = "core_app.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "core_app.wsgi.application"

DATABASES = {"default": env.db()}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
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


LANGUAGE_CODE = "ru-RU"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.UserPublic"

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
        "level": "DEBUG" if env.bool("DEBUG") else "INFO",
    },
    "loggers": {
        "django.db": {
            "handlers": ["console"],
            "level": "DEBUG" if env.bool("DEBUG") else "INFO",
            "propagate": False,
        },
    },
}


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Kapibara API",
    "DESCRIPTION": "API for Kapibara",
    "VERSION": "0.0.1-alpha",
    "SERVE_INCLUDE_SCHEMA": False,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(
        minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", 5)
    ),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(
        days=env.int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", 1)
    ),
    "SIGNING_KEY": env.str("JWT_SIGNING_KEY", SECRET_KEY),
    "USER_ID_FIELD": "external_user_uid",
}

COMMENT_VOTE_RATING_COEFF = env.float("COMMENT_VOTE_RATING_COEFF", 0.5)
