import os

from django.utils.translation import gettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = "l@6boni%5$tg*dzta%6fellmleoum4g*p-1#q64g3hi-0&1@!n"

# DEBUG = bool(os.environ['DEBUG'])
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "http://localhost:3000", "http://127.0.0.1:3000"]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "financez.apps.FinancezConfig",
    "currencies.apps.CurrenciesConfig",
    "registration.apps.RegistrationConfig",  # to be removed
    "users.apps.UsersConfig",
    "accounts.apps.AccountsConfig",
    "entries.apps.EntriesConfig",
    "reports.apps.ReportsConfig",
    "settings.apps.SettingsConfig",
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = ["http://localhost:3000", "http://localhost"]

CSRF_COOKIE_NAME = "csrftoken"
# CSRF_HEADER_NAME = "HTTP_X_CSRFTOKEN"
# CSRF_HEADER_NAME = "X-CSRFToken"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

ROOT_URLCONF = "financez.urls"

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

WSGI_APPLICATION = "financez.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "../db/", "db.sqlite3"),
    }
}


AUTH_PASSWORD_VALIDATORS = []

LOGIN_REDIRECT_URL = LOGOUT_REDIRECT_URL = "/"

LANGUAGE_CODE = "en-us"

LANGUAGES = [
    ("en", _("English")),
    ("ru", _("Russian")),
]


TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATE_FORMAT = "Y n j"

FIRST_DAY_OF_WEEK = 1

STATIC_URL = "/static/"
STATIC_ROOT = "/srv/static/financez/"
