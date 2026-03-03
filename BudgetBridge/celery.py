import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BudgetBridge.settings")

app = Celery("BudgetBridge")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()