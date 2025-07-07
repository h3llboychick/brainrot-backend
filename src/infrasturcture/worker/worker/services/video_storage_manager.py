from ..clients.minio import MinioClient
from ..settings import settings

from datetime import timedelta

class VideoStorageManager:
    def __init__(self, minio_client: MinioClient):
        self.minio_client = minio_client

    def upload_video(
            self, 
            object_name: str, 
            file_path: str, 
            bucket_name: str = settings.MINIO_VIDEOS_BUCKET,
            content_type: str = "application/octet-stream"
        ) -> str:
        self.minio_client.upload_file(
            object_name=object_name,
            file_path=file_path,
            bucket_name=bucket_name,
            content_type=content_type
        )

        return self.get_video_url(
            object_name=object_name,
            bucket_name=bucket_name
        )
    
    def get_video_url(
            self, 
            object_name: str, 
            bucket_name: str = settings.MINIO_VIDEOS_BUCKET,
            expires_hours: int = 1
        ) -> str:
        return self.minio_client.generate_presigned_url(
            object_name=object_name,
            bucket_name=bucket_name,
            expires=timedelta(hours=expires_hours)
        )

def get_video_storage_manager(minio_client: MinioClient) -> VideoStorageManager:
    return VideoStorageManager(minio_client)