"""
Encryption at rest for stored documents.

Every bucket gets a default server-side encryption rule (SSE-S3, AES256), so the storage
server encrypts each object as it is written, whoever writes it: the API, or a browser
through a presigned URL. Clients send no encryption headers and need no keys.

- RustFS (S3_ENDPOINT_URL set): SSE-S3 needs a key in RustFS's built-in KMS, which is
  created here on first start through the RustFS admin API.
- AWS S3: SSE-S3 is already AWS's default; setting it explicitly makes it a guarantee.

Unlike bucket creation, failures here are fatal: the API must not start and silently
store unencrypted documents.
"""

import asyncio
import hashlib

import boto3
import httpx
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials

from app.core.config import settings
from app.logs.logger import docflow_logger as logger

# RustFS encrypts SSE-S3 objects with the KMS key named "default" unless
# RUSTFS_KMS_DEFAULT_KEY_ID points elsewhere.
RUSTFS_SSE_KEY_ID = "default"

_SSE_S3_RULE = {
    "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
}
_EMPTY_BODY_SHA256 = hashlib.sha256(b"").hexdigest()


async def _rustfs_admin(
    client: httpx.AsyncClient, method: str, path: str
) -> httpx.Response:
    """Call the RustFS admin API, which uses the same SigV4 signing as S3."""

    url = f"{settings.s3_endpoint_url}/rustfs/admin/v3{path}"
    request = AWSRequest(
        method=method,
        url=url,
        data=b"",
        headers={"x-amz-content-sha256": _EMPTY_BODY_SHA256},
    )
    SigV4Auth(
        Credentials(settings.aws_access_key_id, settings.aws_secret_key),
        "s3",
        settings.aws_region,
    ).add_auth(request)

    return await client.request(method, url, headers=dict(request.headers), content=b"")


async def _ensure_rustfs_kms_key() -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await _rustfs_admin(client, "GET", f"/kms/keys/{RUSTFS_SSE_KEY_ID}")
        if response.status_code == 200:
            logger.info(f"✅ RustFS KMS key '{RUSTFS_SSE_KEY_ID}' already exists")
            return
        if response.status_code != 404:
            raise RuntimeError(
                f"Could not check RustFS KMS key '{RUSTFS_SSE_KEY_ID}' "
                f"({response.status_code}): {response.text[:300]}. "
                "Is KMS enabled on RustFS (RUSTFS_KMS_ENABLE)?"
            )

        response = await _rustfs_admin(
            client, "POST", f"/kms/create-key?key-id={RUSTFS_SSE_KEY_ID}"
        )
        # 409: created concurrently by another API instance
        if response.status_code not in (200, 409):
            raise RuntimeError(
                f"Could not create RustFS KMS key '{RUSTFS_SSE_KEY_ID}' "
                f"({response.status_code}): {response.text[:300]}"
            )
        logger.info(f"✅ Created RustFS KMS key '{RUSTFS_SSE_KEY_ID}'")


def _apply_bucket_encryption(buckets: list[str]) -> None:
    config = {
        "aws_access_key_id": settings.aws_access_key_id,
        "aws_secret_access_key": settings.aws_secret_key,
        "region_name": settings.aws_region,
    }
    if settings.s3_endpoint_url:
        config["endpoint_url"] = settings.s3_endpoint_url
    client = boto3.client("s3", **config)

    for bucket in buckets:
        client.put_bucket_encryption(
            Bucket=bucket, ServerSideEncryptionConfiguration=_SSE_S3_RULE
        )
        rules = client.get_bucket_encryption(Bucket=bucket)[
            "ServerSideEncryptionConfiguration"
        ]["Rules"]
        algorithm = rules[0]["ApplyServerSideEncryptionByDefault"]["SSEAlgorithm"]
        if algorithm != "AES256":
            raise RuntimeError(
                f"Bucket '{bucket}' reports encryption {algorithm!r}, expected AES256"
            )
        logger.info(f"🔒 Encryption at rest (SSE-S3) enforced on bucket '{bucket}'")


async def ensure_bucket_encryption() -> None:
    """Make sure every document bucket encrypts new objects at rest. Raises on failure."""

    if settings.s3_endpoint_url:
        await _ensure_rustfs_kms_key()

    buckets = [settings.s3_bucket]
    if settings.s3_test_bucket and settings.s3_test_bucket != settings.s3_bucket:
        buckets.append(settings.s3_test_bucket)

    await asyncio.to_thread(_apply_bucket_encryption, buckets)
