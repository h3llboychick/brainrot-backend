import enum


class VideoJobStatus(enum.Enum):
    queued = "queued"
    processing = "processing"
    done = "done"
    published = "published"
    failed = "failed"
    cancelled = "cancelled"
