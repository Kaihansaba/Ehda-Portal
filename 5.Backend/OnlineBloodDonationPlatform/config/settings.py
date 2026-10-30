import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_file(path):
    """
    Read KEY=VALUE lines from an optional .env file into os.environ.

    Real environment variables always win. No extra package needed.
    See .env.example for the supported settings.
    """
    if not path.exists():
        return

    for line in path.read_text().splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


load_env_file(BASE_DIR / ".env")


def env_bool(name, default):
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def env_list(name):
    """A comma-separated environment variable as a list, e.g. "a.com, b.com"."""
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]


# Development defaults: the app runs with no environment variables set.
DEV_SECRET_KEY = "django-insecure-dev-only-change-this-in-production"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", DEV_SECRET_KEY)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_bool("DJANGO_DEBUG", True)

# Comma-separated, e.g. "ehdaportal.pythonanywhere.com".
# Empty is fine while DEBUG is on (localhost is allowed automatically).
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")

# Comma-separated full origins, e.g. "https://ehdaportal.pythonanywhere.com".
# Needed for forms (CSRF) when the site is served over HTTPS.
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

# Placeholder values (the dev key, .env.example's "change-me", or an
# empty value) must never be used in production.
INSECURE_SECRET_KEYS = {DEV_SECRET_KEY, "change-me", ""}

if not DEBUG and SECRET_KEY.strip() in INSECURE_SECRET_KEYS:
    raise ImproperlyConfigured(
        "Set DJANGO_SECRET_KEY to a long random value when DJANGO_DEBUG is off."
    )


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Our application
    "accounts.apps.AccountsConfig",
    "locations.apps.LocationsConfig",
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


ROOT_URLCONF = "config.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        # Our project-level templates folder
        "DIRS": [BASE_DIR / "templates"],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "accounts.context_processors.request_badges",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = "static/"

# Project-level static files (CSS, JS, icons). Served automatically by
# runserver while DEBUG is True.
STATICFILES_DIRS = [BASE_DIR / "static"]

# Where "python manage.py collectstatic" copies every static file for the
# web server (PythonAnywhere's static files mapping points here).
STATIC_ROOT = BASE_DIR / "staticfiles"


# Default primary key field type
# https://docs.djangoproject.com/en/6.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Custom user model
AUTH_USER_MODEL = "accounts.User"


# Login URL
LOGIN_URL = "/login/"


# Email
# Without SMTP settings, emails are printed to the console (the terminal
# running the server, or the server log on PythonAnywhere). Setting
# EMAIL_HOST_USER and EMAIL_HOST_PASSWORD switches to SMTP. Sending never
# breaks a page: failures are logged (config/email.py and
# accounts/notifications.py). PythonAnywhere's free tier blocks SMTP.
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_TIMEOUT = int(os.environ.get("EMAIL_TIMEOUT", "10"))
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "webmaster@localhost")

SMTP_CONFIGURED = bool(EMAIL_HOST_USER and EMAIL_HOST_PASSWORD)
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND") or (
    "config.email.SafeSMTPEmailBackend" if SMTP_CONFIGURED
    else "django.core.mail.backends.console.EmailBackend"
)


# Send our site's origin (not the full URL) as the Referer to other sites.
# OpenStreetMap's tile servers return 403 for requests without one.
# Django's default ("same-origin") sends no Referer to other sites.
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"


# Production (DEBUG off), e.g. on PythonAnywhere
# PythonAnywhere terminates HTTPS and forwards requests to Django over
# HTTP with X-Forwarded-Proto set. "Force HTTPS" in its Web tab does the
# redirect, so Django's own SECURE_SSL_REDIRECT stays off by default.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", False)
    # Optional: tell browsers to use HTTPS only (e.g. 3600, later 31536000).
    # Turn it on only after HTTPS works, because browsers remember it.
    SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "0"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", True)

    SILENCED_SYSTEM_CHECKS = [
        # HSTS preload is only for sites on their own registered domain,
        # not a subdomain such as ehdaportal.pythonanywhere.com.
        "security.W021",
    ]
    if not SECURE_SSL_REDIRECT:
        # The redirect is done by PythonAnywhere ("Force HTTPS").
        SILENCED_SYSTEM_CHECKS.append("security.W008")


# Logging
# Errors (and email failures) go to the console, which is the server log
# on PythonAnywhere ("Error log" link in the Web tab).
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("DJANGO_LOG_LEVEL", "WARNING"),
    },
}
