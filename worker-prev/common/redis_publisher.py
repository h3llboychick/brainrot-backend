import redis
import json


def update_status(r: redis.Redis, key: str, status: dict) -> None:
    try:
        r.set(key, json.dumps(status).encode())
        updates_payload = {
            "video_id": status["video_id"],
            "status": status["status"],
            "video_url": status.get("video_url", None),
        }
        r.xadd("updates:videos", {"data": json.dumps(updates_payload).encode()})
        return True
    except redis.ConnectionError as e:
        print("Redis connection error:", e)
    except Exception as e:
        print("Error publishing message to Redis:", e)
    return False
