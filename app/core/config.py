import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class GlobalConfig(BaseSettings):
    """
    Global Configuration for the FastAPI application.
    """

    title: str = os.environ.get("TITLE")
    version: str = "1.0.0"
    description: str = os.environ.get("DESCRIPTION")
    host_url: str = "http://localhost:8000"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    api_prefix: str = "/v2"
    debug: bool = str(os.environ.get("DEBUG", "False")).lower() == "true"
    postgres_user: str = os.environ.get("POSTGRES_USER")
    postgres_password: str = os.environ.get("POSTGRES_PASSWORD")
    postgres_hostname: str = os.environ.get("DATABASE_HOSTNAME")
    postgres_port: int = int(os.environ.get("POSTGRES_PORT"))
    postgres_db: str = os.environ.get("POSTGRES_DB")
    db_echo_log: bool = str(os.environ.get("DEBUG", "False")).lower() == "true"
    aws_access_key_id: str = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_key: str = os.environ.get("AWS_SECRET_ACCESS_KEY")
    aws_region: str = os.environ.get("AWS_REGION")
    s3_bucket: str = os.environ.get("S3_BUCKET")
    s3_test_bucket: str = os.environ.get("S3_TEST_BUCKET")
    # user config
    access_token_expire_min: int = os.environ.get("ACCESS_TOKEN_EXPIRE_MIN")
    refresh_token_expire_min: int = os.environ.get("REFRESH_TOKEN_EXPIRE_MIN")
    algorithm: str = os.environ.get("ALGORITHM")
    jwt_secret_key: str = os.environ.get("JWT_SECRET_KEY")
    jwt_refresh_secret_key: str = os.environ.get("JWT_REFRESH_SECRET_KEY")
    # Email Service
    smtp_server: str = os.environ.get("SMTP_SERVER")
    smtp_port: int = os.environ.get("SMTP_PORT")
    email: str = os.environ.get("EMAIL")
    app_pw: str = os.environ.get("APP_PASSWORD")

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
