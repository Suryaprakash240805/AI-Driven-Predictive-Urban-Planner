import io, os
from minio import Minio

_client = Minio(
    os.getenv("MINIO_ENDPOINT","localhost:9000"),
    access_key=os.getenv("MINIO_ACCESS_KEY","minioadmin"),
    secret_key=os.getenv("MINIO_SECRET_KEY","minioadmin"),
    secure=False,
)
BUCKET = os.getenv("MINIO_BUCKET_LAYOUTS","urban-layouts")

def upload_layout_image(data: bytes, filename: str) -> str:
    if not _client.bucket_exists(BUCKET):
        _client.make_bucket(BUCKET)
    _client.put_object(BUCKET, filename, io.BytesIO(data),
                        length=len(data), content_type="image/png")
    endpoint = os.getenv("MINIO_ENDPOINT","localhost:9000")
    return f"http://{endpoint}/{BUCKET}/{filename}"
