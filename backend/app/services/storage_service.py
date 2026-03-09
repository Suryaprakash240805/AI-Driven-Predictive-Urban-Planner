import io
from minio import Minio
from minio.error import S3Error
from app.config import settings

_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False,
)

def _ensure_bucket(bucket: str):
    if not _client.bucket_exists(bucket):
        _client.make_bucket(bucket)

def upload_pdf(data: bytes, filename: str) -> str:
    _ensure_bucket(settings.MINIO_BUCKET_REPORTS)
    _client.put_object(
        settings.MINIO_BUCKET_REPORTS, filename,
        io.BytesIO(data), length=len(data),
        content_type="application/pdf"
    )
    return f"http://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET_REPORTS}/{filename}"

def upload_image(data: bytes, filename: str) -> str:
    _ensure_bucket(settings.MINIO_BUCKET_LAYOUTS)
    _client.put_object(
        settings.MINIO_BUCKET_LAYOUTS, filename,
        io.BytesIO(data), length=len(data),
        content_type="image/png"
    )
    return f"http://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET_LAYOUTS}/{filename}"

def get_object_bytes(bucket: str, filename: str) -> bytes:
    resp = _client.get_object(bucket, filename)
    return resp.read()
