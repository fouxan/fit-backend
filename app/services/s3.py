from __future__ import annotations
import boto3
from botocore.config import Config
from typing import BinaryIO, Optional
from app.models.s3 import PresignedURL
from app.config import settings

settings = settings.get_settings()


class S3Service:
    def __init__(self):
        session_kwargs = {}
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            session_kwargs.update(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )

        s3_config = Config(
            region_name=settings.AWS_REGION,
            retries={"max_attempts": 5, "mode": "standard"},
        )

        self._client = boto3.client(
            "s3",
            config=s3_config,
            **session_kwargs,
        )
        self.bucket = settings.S3_EXERCISE_CATALOG_BUCKET

    def upload_fileobj(
        self,
        fileobj: BinaryIO,
        key: str,
        content_type: Optional[str] = None,
        acl: Optional[str] = None,  # e.g. "private" (default) or "public-read"
        cache_control: Optional[str] = None,
    ) -> str:
        extra = {}
        if content_type:
            extra["ContentType"] = content_type
        if acl:
            extra["ACL"] = acl
        if cache_control:
            extra["CacheControl"] = cache_control

        self._client.upload_fileobj(fileobj, self.bucket, key, ExtraArgs=extra or None)
        return key

    def download_fileobj(self, key: str, fileobj: BinaryIO) -> None:
        self._client.download_fileobj(self.bucket, key, fileobj)

    def get_object_stream(self, key: str):
        """Returns a streaming body; caller must .read() or iterate."""
        res = self._client.get_object(Bucket=self.bucket, Key=key)
        return res["Body"], res.get("ContentType"), res.get("ContentLength")

    def presign_put(
        self, key: str, expires_in: int = 900, content_type: Optional[str] = None
    ) -> PresignedURL:
        params = {"Bucket": self.bucket, "Key": key}
        if content_type:
            params["ContentType"] = content_type
        url = self._client.generate_presigned_url(
            ClientMethod="put_object",
            Params=params,
            ExpiresIn=expires_in,
        )
        return PresignedURL(url=url, method="PUT", key=key, expires_in=expires_in)

    def presign_get(self, key: str, expires_in: int = 900) -> PresignedURL:
        url = self._client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        return PresignedURL(url=url, method="GET", key=key, expires_in=expires_in)

    def delete(self, key: str) -> None:
        self._client.delete_object(Bucket=self.bucket, Key=key)

    def list(self, prefix: str = "") -> list[str]:
        keys: list[str] = []
        paginator = self._client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for item in page.get("Contents", []):
                keys.append(item["Key"])
        return keys
