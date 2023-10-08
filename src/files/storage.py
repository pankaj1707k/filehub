from datetime import timedelta
from functools import wraps
from typing import Any, Callable

from django.conf import settings
from minio import Minio


class S3:
    """
    Storage class for S3. A wrapper over Minio SDK.
    """

    client = Minio(
        endpoint=settings.S3_ENDPOINT_URL,
        access_key=settings.S3_ACCESS_KEY,
        secret_key=settings.S3_SECRET_KEY,
        secure=settings.S3_SECURE_CONNECTION,
    )

    @staticmethod
    def check_bucket_exists(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(self, *args, **kwargs) -> Any:
            if not S3.client.bucket_exists(settings.S3_BUCKET):
                S3.client.make_bucket(settings.S3_BUCKET)
            return method(self, *args, **kwargs)

        return wrapper

    @check_bucket_exists
    def get_upload_url(self, key: str, time: int = 300) -> str:
        return self.client.presigned_put_object(
            settings.S3_BUCKET, key, timedelta(seconds=time)
        )

    @check_bucket_exists
    def get_download_url(self, key: str, time: int = 300) -> str:
        return self.client.presigned_get_object(
            settings.S3_BUCKET, key, timedelta(seconds=time)
        )

    def delete_file(self, key: str) -> None:
        return self.client.remove_object(settings.S3_BUCKET, key)
