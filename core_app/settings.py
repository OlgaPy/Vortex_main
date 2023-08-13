import datetime
from pathlib import Path

import environ

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = env.str(
    "SECRET_KEY", "django-insecure-34oqj72*yq6cky9nrubxyaw1^hvyybp&7=+uw%f-6wac%og4pn"
)

DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", str, ["*"])

DJANGO_APPS = [
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
    "django_otp",
    "django_otp.plugins.otp_static",
    "django_otp.plugins.otp_totp",
    "two_factor",
]

KAPIBARA_APPS = [
    "users",
    "posts",
    "communities",
    "core_app.apps.KapibaraAdminConfig",
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
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if env.bool("ENABLE_DB_STATS", default=False):
    MIDDLEWARE += ["common.middlewares.DBStatsMiddleware"]

ROOT_URLCONF = "core_app.urls"

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

WSGI_APPLICATION = "core_app.wsgi.application"

DATABASES = {"default": env.db()}

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
        "level": "DEBUG" if DEBUG else "INFO",
    },
    "loggers": {
        "django.db": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}

LOGIN_URL = "two_factor:login"

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

RSA_PRIVATE_KEY = env.str("RSA_PRIVATE_KEY", SECRET_KEY)
RSA_PUBLIC_KEY = env.str("RSA_PUBLIC_KEY", "")
SIMPLE_JWT = {
    "ALGORITHM": "RS512" if RSA_PRIVATE_KEY and RSA_PUBLIC_KEY else "HS256",
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(
        minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", 5)
    ),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(
        days=env.int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", 1)
    ),
    "SIGNING_KEY": RSA_PRIVATE_KEY,
    "VERIFYING_KEY": RSA_PUBLIC_KEY,
    "USER_ID_FIELD": "external_user_uid",
}

TWO_FACTOR_PATCH_ADMIN = env.bool("ENABLE_DJANGO_ADMIN_OTP", True)
DJANGO_ADMIN_PATH = env.str("DJANGO_ADMIN_PATH", "admin")
COMMENT_VOTE_RATING_COEFF = env.float("COMMENT_VOTE_RATING_COEFF", 0.5)
