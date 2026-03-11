# BudgetBridge/settings/docker.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Database for Docker
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "budgetbridge_db"),
        "USER": os.getenv("POSTGRES_USER", "budgetbridge_user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "12345678"),
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

# Celery for Docker
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://redis:6379/0")
