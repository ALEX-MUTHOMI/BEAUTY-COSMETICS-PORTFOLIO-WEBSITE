import os

from celery import Celery, Task

from core.middleware.correlation_id import get_correlation_id

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")


class CorrelatedTask(Task):
    def apply_async(self, args=None, kwargs=None, **options):
        kwargs = dict(kwargs or {})
        kwargs.setdefault("correlation_id", get_correlation_id())
        return super().apply_async(args=args, kwargs=kwargs, **options)


app.Task = CorrelatedTask

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
