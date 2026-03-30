from datetime import timedelta

from minio import Minio

from ..settings import settings


class MinioClient:
    def __init__(self, endpoint, access_key, secret_key, secure=False):
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

    def upload_file(
        self,
        object_name: str,
        file_path: str,
        bucket_name: str,
        content_type: str,
    ):
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

        result = self.client.fput_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=file_path,
            content_type=content_type,
        )
        return result

    def generate_presigned_url(
        self,
        object_name: str,
        bucket_name: str = settings.MINIO_VIDEOS_BUCKET,
        expires=timedelta(hours=1),
    ):
        url = self.client.presigned_get_object(
            bucket_name=bucket_name, object_name=object_name, expires=expires
        )
        return url


def get_minio_client() -> MinioClient:
    return MinioClient(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )
