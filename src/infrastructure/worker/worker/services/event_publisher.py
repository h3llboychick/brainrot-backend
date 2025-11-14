from redis import Redis

from celery.utils.log import get_logger
import json


logger = get_logger(__name__)


class EventPublisher:
    def __init__(self, client: Redis):
        self.client = client
        
    def publish_event(self, job_id: str, event: str, **payload) -> None:
        message = {"job_id": job_id, "event": event, **payload}
        logger.info(f"EVENT {event} | job_id={job_id} | payload={payload}")
        try:
            self.client.publish(f"video_job:{job_id}", json.dumps(message, ensure_ascii=False))
        except Exception:
            logger.warning("Failed to publish event to Redis", exc_info=True)

    def close(self):
        self.client.close()


def get_event_publisher(redis_client: Redis) -> EventPublisher:
    return EventPublisher(redis_client)

