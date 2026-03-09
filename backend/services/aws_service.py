from datetime import datetime
from uuid import uuid4

import boto3

from app.config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    AWS_BUCKET,
    AWS_S3_PREFIX,
)


def _get_s3_client():
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY or not AWS_REGION:
        raise ValueError("AWS credentials or region are not configured")

    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )


def _build_object_key(filename: str, folder: str = "analysis"):
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid4().hex[:8]
    safe_filename = filename.replace("\\", "_").replace("/", "_")

    prefix = (AWS_S3_PREFIX or "wafer").strip("/")

    return f"{prefix}/{folder}/{timestamp}_{unique_id}_{safe_filename}"


def upload_bytes(data: bytes, filename: str, folder: str = "analysis", content_type: str | None = None):
    if not AWS_BUCKET:
        raise ValueError("AWS_BUCKET is not configured")

    if not data:
        raise ValueError("No data provided for upload")

    s3 = _get_s3_client()
    key = _build_object_key(filename=filename, folder=folder)

    extra_args = {}
    if content_type:
        extra_args["ContentType"] = content_type

    try:
        s3.put_object(
            Bucket=AWS_BUCKET,
            Key=key,
            Body=data,
            **extra_args,
        )
    except Exception as exc:
        raise RuntimeError(f"S3 upload failed: {exc}") from exc

    return f"https://{AWS_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"


def generate_presigned_url(object_key: str, expires_in: int = 3600):
    if not AWS_BUCKET:
        raise ValueError("AWS_BUCKET is not configured")

    s3 = _get_s3_client()

    try:
        return s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": AWS_BUCKET,
                "Key": object_key,
            },
            ExpiresIn=expires_in,
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to generate presigned URL: {exc}") from exc