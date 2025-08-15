from typing import List, Union
from pydantic import AnyHttpUrl, field_validator, EmailStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets
from functools import lru_cache


class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = Field("Fit API", env="APP_NAME")
    VERSION: str = Field("0.1.0", env="VERSION")
    DEBUG: bool = Field(True, env="DEBUG")

    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # Security
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY"
    )
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default_factory=list, env="BACKEND_CORS_ORIGINS"
    )

    # Google OAuth2
    GOOGLE_CLIENT_ID: str = Field(..., env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(..., env="GOOGLE_CLIENT_SECRET")

    # Email settings
    MAIL_USERNAME: str = Field(..., env="MAIL_USERNAME")
    MAIL_PASSWORD: str = Field(..., env="MAIL_PASSWORD")
    MAIL_FROM: EmailStr = Field(..., env="MAIL_FROM")
    MAIL_PORT: int = Field(587, env="MAIL_PORT")
    MAIL_SERVER: str = Field(..., env="MAIL_SERVER")
    MAIL_STARTTLS: bool = Field(True, env="MAIL_STARTTLS")
    MAIL_SSL_TLS: bool = Field(False, env="MAIL_SSL_TLS")
    MAIL_USE_CREDENTIALS: bool = Field(True, env="MAIL_USE_CREDENTIALS")

    # Redis
    REDIS_URL: str = Field("redis://localhost:6379", env="REDIS_URL")

    # Stripe
    STRIPE_SECRET_KEY: str = Field(..., env="STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY: str = Field(..., env="STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET: str = Field(..., env="STRIPE_WEBHOOK_SECRET")

    # AWS / S3
    AWS_REGION: str = Field(..., env="AWS_REGION")
    AWS_ACCESS_KEY_ID: str | None = Field(None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str | None = Field(None, env="AWS_SECRET_ACCESS_KEY")
    # S3_BUCKET: str = Field(..., env="S3_BUCKET")
    S3_EXERCISE_CATALOG_BUCKET: str = Field(..., env="S3_EXERCISE_CATALOG_BUCKET")

    # Frontend URL for email links
    FRONTEND_URL: str = Field("http://localhost:3000", env="FRONTEND_URL")

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
