# import os
# from celery import Celery

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BudgetBridge.settings")

# app = Celery("BudgetBridge")

# app.config_from_object("django.conf:settings", namespace="CELERY")

# app.autodiscover_tasks()



import os
from celery import Celery


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.getenv("DJANGO_SETTINGS_MODULE", "BudgetBridge.settings.local")
)

app = Celery("BudgetBridge")

# Load settings with CELERY_ prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from installed apps
app.autodiscover_tasks()

# Optional: log startup info
@app.task(bind=True)
def debug_task(self):
    print(f"Celery worker started! Task id: {self.request.id}")