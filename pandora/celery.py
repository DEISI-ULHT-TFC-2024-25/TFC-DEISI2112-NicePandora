import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pandora.settings')

# Use the environment variable or a default value for the broker URL.
broker_url = os.environ.get("CELERY_BROKER", "redis://redis:6379/0")

# Initialize the Celery app with the correct broker URL.
#app = Celery('pandora', broker=broker_url)
app = Celery("pandora")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')


#app.conf.update(
#    broker_url="redis://redis:6379/0",
#    result_backend="redis://redis:6379/0",
#    task_always_eager=False,
#    task_publish_retry=True,
#    task_publish_retry_policy={
#        "max_retries": 5,
#        "interval_start": 0,
#        "interval_step": 1,
#        "interval_max": 3,
#    },
#)


# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')




