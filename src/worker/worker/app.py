from celery import Celery
from kombu import Exchange, Queue

app = Celery(
    "worker",
    include=[
        "worker.tasks.generate_video",
        "worker.tasks.publish_video",
    ],
)
app.config_from_object("worker.config")

video_exchange = Exchange("video", type="topic", durable=True)

app.conf.task_queues = (
    Queue(
        name="video.generate",
        exchange=video_exchange,
        routing_key="video.generate.*",
        durable=True,
    ),
    Queue(
        name="video.publish",
        exchange=video_exchange,
        routing_key="video.publish.*",
        durable=True,
    ),
    Queue(
        name="video.billing",
        exchange=video_exchange,
        routing_key="video.billing.*",
        durable=True,
    ),
)

app.autodiscover_tasks()
