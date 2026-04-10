import os
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class GlobalConfig(BaseSettings):
    """
    Global Configuration for the FastAPI application.
    """

    title: str = os.environ.get("TITLE", "DocFlow")
    version: str = "1.0.0"
    description: str = os.environ.get("DESCRIPTION", "Document Management API")
    host_url: str = "http://localhost:8000"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    api_prefix: str = "/v2"
    debug: bool = str(os.environ.get("DEBUG", "False")).lower() == "true"
    postgres_user: str = os.environ.get("POSTGRES_USER", "")
    postgres_password: str = os.environ.get("POSTGRES_PASSWORD", "")
    postgres_hostname: str = os.environ.get("DATABASE_HOSTNAME", "")
    postgres_port: int = int(os.environ.get("POSTGRES_PORT", "5432"))
    postgres_db: str = os.environ.get("POSTGRES_DB", "")
    # s3 / minio configurations
    aws_access_key_id: str = os.environ.get("AWS_ACCESS_KEY_ID", "")
    aws_secret_key: str = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.environ.get("AWS_REGION", "us-east-1")  # minio doesn't care about a region
    s3_endpoint_url: Optional[str] = os.environ.get("S3_ENDPOINT_URL") or None
    s3_bucket: str = os.environ.get("S3_BUCKET", "")
    s3_test_bucket: Optional[str] = os.environ.get("S3_TEST_BUCKET") or None
    # user config
    access_token_expire_min: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MIN", "30"))
    refresh_token_expire_min: int = int(os.environ.get("REFRESH_TOKEN_EXPIRE_MIN", "1440"))
    algorithm: str = os.environ.get("ALGORITHM", "HS256")
    jwt_secret_key: str = os.environ.get("JWT_SECRET_KEY", "")
    jwt_refresh_secret_key: str = os.environ.get("JWT_REFRESH_SECRET_KEY", "")
    # Email Service
    smtp_server: str = os.environ.get("SMTP_SERVER", "")
    smtp_port: int = int(os.environ.get("SMTP_PORT", "587"))
    email: str = os.environ.get("EMAIL", "")
    app_pw: str = os.environ.get("APP_PASSWORD", "")

    @property
    def db_echo_log(self) -> bool:
        return self.debug

    @property
    def sync_database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_hostname}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def async_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_hostname}:{self.postgres_port}/{self.postgres_db}"
        )


settings = GlobalConfig()
