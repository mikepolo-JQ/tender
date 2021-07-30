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
    "update-data-every-day-at-midnight": {
        "task": "offer.tasks.update_data_file",
        "schedule": crontab(minute=0, hour=0),
    },
    # Executes every day at 00:01
    "upload-data-to-the-DB-every-day-at-00-01": {
        "task": "offer.tasks.upload_data_from_file_to_the_db",
        "schedule": crontab(minute=1, hour=0),
    },
}
