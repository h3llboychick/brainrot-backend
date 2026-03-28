"""
Minimal Celery app used by the API to dispatch tasks to the worker.

This module does NOT import any worker task implementations — it only
connects to the broker so that `app.send_task()` can place messages on
the queue for the actual worker process to consume.
"""

from celery import Celery
from src.settings import settings

app = Celery(broker=settings.CELERY_BROKER_URL)

# Mirror the same serialization settings as the worker
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    task_ignore_result=True,
)
