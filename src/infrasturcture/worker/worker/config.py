from .settings import settings

broker_url=settings.CELERY_BROKER_URL

accept_content = ['json']

task_serializer = 'json'
task_ignore_result = True

task_router = {
    'generate_video': {
        'queue': 'video.generate',
        'exchange': 'video',
        'routing_key': 'video.generate',
    },
    'publish_video': {
        'queue': 'video.publish',
        'exchange': 'video',
        'routing_key': 'video.publish',
    },
}

worker_prefetch_multiplier = 1