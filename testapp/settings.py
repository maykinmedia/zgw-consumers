import os

DEBUG = True

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = "so-secret-i-cant-believe-you-are-looking-at-this"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv("DB_HOST", ""),
        "NAME": os.getenv("DB_NAME", "zgw_consumers"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
    },
}

# used to connect to the administrative database to check the amount of connections
# in tests/test_concurrency.py
POSTGRES_CONN_PARAMS = {
    "ENGINE": "django.db.backends.postgresql",
    "HOST": os.getenv("DB_HOST", ""),
    "NAME": "postgres",
    "USER": os.getenv("DB_USER", "postgres"),
    "PASSWORD": os.getenv("DB_PASSWORD", ""),
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
}

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "zgw_consumers",
    "simple_certmanager",
    "solo",
    "testapp",
    "django_setup_configuration",
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
            ]
        },
    }
]

ROOT_URLCONF = "testapp.urls"

STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"
