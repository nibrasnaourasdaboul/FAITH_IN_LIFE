import uuid
from pathlib import Path

from app.core.config import get_settings

BUCKETS = ("avatars", "licenses", "clinical-documents", "imaging", "exercise-media", "reports")


class StorageService:
    # يجهّز مخزن الملفات المحلي أو مخزن مينيو.
    def __init__(self) -> None:
        self.settings = get_settings()
        self.root = Path(self.settings.storage_root)

    # ينشئ مجلدات التخزين عند الإقلاع.
    def ensure_layout(self) -> None:
        for bucket in BUCKETS:
            (self.root / bucket).mkdir(parents=True, exist_ok=True)
        if self.settings.storage_backend == "minio":
            self._ensure_minio_buckets()

    # يفتح عميل مينيو عند اختيار هذا المخزن.
    def _client(self):
        from minio import Minio

        return Minio(
            self.settings.minio_endpoint,
            access_key=self.settings.minio_access_key,
            secret_key=self.settings.minio_secret_key,
            secure=self.settings.minio_secure,
        )

    # ينشئ الحاويات الناقصة في مينيو.
    def _ensure_minio_buckets(self) -> None:
        client = self._client()
        for bucket in BUCKETS:
            if not client.bucket_exists(bucket):
                client.make_bucket(bucket)

    # يحفظ الملف ويُرجع مفتاح الوصول إليه.
    def save_bytes(self, bucket: str, filename: str, data: bytes, content_type: str) -> str:
        if bucket not in BUCKETS:
            raise ValueError("unknown_bucket")
        key = f"{uuid.uuid4().hex}-{Path(filename).name}"
        if self.settings.storage_backend == "minio":
            from io import BytesIO

            self._client().put_object(bucket, key, BytesIO(data), length=len(data), content_type=content_type)
            return f"s3://{bucket}/{key}"

        destination = self.root / bucket / key
        destination.write_bytes(data)
        if bucket == "avatars":
            return f"/media/avatars/{key}"
        return f"local://{bucket}/{key}"


storage = StorageService()
