import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

app = Celery("project")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


# Celery beat
app.conf.beat_schedule = {
    # Executes every day at 00:00
    'update-data-every-day-at-midnight': {
        'task': 'offer.tasks.update_data_file',
        'schedule': crontab(minute=0, hour=0),
    },
}
