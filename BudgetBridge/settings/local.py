# BudgetBridge/settings/local.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "budgetbridge_db"),
        "USER": os.getenv("DB_USER", "budgetbridge_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", "12345678"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# Celery settings for local dev (using Redis)
CELERY_BROKER_URL = os.getenv("REDIS_URL_local", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL_local", "redis://localhost:6379/0")