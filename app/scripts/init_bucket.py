import asyncio

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings
from app.logs.logger import s3_logger


async def create_bucket_if_not_exists():
    """Create S3/MinIO bucket if it doesn't exist"""
    try:
        boto3_config = {
            'aws_access_key_id': settings.aws_access_key_id,
            'aws_secret_access_key': settings.aws_secret_key,
            'region_name': settings.aws_region,
        }

        if settings.s3_endpoint_url:
            boto3_config['endpoint_url'] = settings.s3_endpoint_url

        client = boto3.client('s3', **boto3_config)

        try:
            client.head_bucket(Bucket=settings.s3_bucket)
            s3_logger.info(f"✅ Bucket '{settings.s3_bucket}' already exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                try:
                    if settings.s3_endpoint_url:
                        client.create_bucket(Bucket=settings.s3_bucket)
                    else:
                        if settings.aws_region == 'us-east-1':
                            client.create_bucket(Bucket=settings.s3_bucket)
                        else:
                            client.create_bucket(
                                Bucket=settings.s3_bucket,
                                CreateBucketConfiguration={'LocationConstraint': settings.aws_region}
                            )

                    s3_logger.info(f"✅ Created bucket '{settings.s3_bucket}'")

                    await asyncio.sleep(1)          # waiting for bucket to get created

                    try:
                        client.put_bucket_versioning(
                            Bucket=settings.s3_bucket,
                            VersioningConfiguration={'Status': 'Enabled'}
                        )
                        s3_logger.info(f"✅ Enabled versioning for bucket '{settings.s3_bucket}'")
                    except Exception as ve:
                        s3_logger.warning(f"⚠️  Could not enable versioning: {ve}")

                except ClientError as ce:
                    s3_logger.warning(f"❌ Failed to create bucket '{settings.s3_bucket}': {ce}")
                    raise
            else:
                s3_logger.warning(f"❌ Error accessing bucket '{settings.s3_bucket}': {e}")
                raise

        # Also create test bucket if specified and different from main bucket
        if settings.s3_test_bucket and settings.s3_test_bucket != settings.s3_bucket:
            try:
                client.head_bucket(Bucket=settings.s3_test_bucket)
                s3_logger.info(f"✅ Test bucket '{settings.s3_test_bucket}' already exists")
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    try:
                        if settings.s3_endpoint_url:
                            client.create_bucket(Bucket=settings.s3_test_bucket)
                        else:
                            if settings.aws_region == 'us-east-1':
                                client.create_bucket(Bucket=settings.s3_test_bucket)
                            else:
                                client.create_bucket(
                                    Bucket=settings.s3_test_bucket,
                                    CreateBucketConfiguration={'LocationConstraint': settings.aws_region}
                                )
                        s3_logger.info(f"✅ Created test bucket '{settings.s3_test_bucket}'")
                    except ClientError as ce:
                        s3_logger.warning(f"❌ Failed to create test bucket '{settings.s3_test_bucket}': {ce}")

    except Exception as e:
        s3_logger.warning(f"❌ Error during bucket initialization: {e}")
