from typing import List, Union
from pydantic import AnyHttpUrl, field_validator, EmailStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets
from functools import lru_cache
import logging
import json


# Optional JSON formatter (used when LOG_JSON=True)
class CustomJSONFormatter(logging.Formatter):
    def __init__(self, fmt: str = "%(asctime)s"):
        super().__init__(fmt=fmt)

    def format(self, record: logging.LogRecord) -> str:
        # ensure base fields (like asctime/message) are populated
        super().format(record)
        payload = {
            "time": getattr(record, "asctime", None),
            "process_name": record.processName,
            "process_id": record.process,
            "thread_name": record.threadName,
            "thread_id": record.thread,
            "level": record.levelname,
            "logger_name": record.name,
            "pathname": record.pathname,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        # If you log with: logger.info("msg", extra={"extra_info": {...}})
        if hasattr(record, "extra_info"):
            extra = getattr(record, "extra_info")
            if isinstance(extra, dict):
                payload["extra"] = extra
        return json.dumps(payload, ensure_ascii=False)

def _upper_or_default(v: str | None, default: str) -> str:
    return (v or default).upper()


class Settings(BaseSettings):
    # ---------- App ----------
    APP_NAME: str = Field("Fit API", env="APP_NAME")
    VERSION: str = Field("0.1.0", env="VERSION")
    DEBUG: bool = Field(True, env="DEBUG")
    ENV: str = Field("development", env="ENV")

    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # ---------- Security / Auth ----------
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # ---------- CORS ----------
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(default_factory=list, env="BACKEND_CORS_ORIGINS")

    # ---------- OAuth / Mail ----------
    GOOGLE_CLIENT_ID: str = Field(..., env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(..., env="GOOGLE_CLIENT_SECRET")

    MAIL_USERNAME: str = Field(..., env="MAIL_USERNAME")
    MAIL_PASSWORD: str = Field(..., env="MAIL_PASSWORD")
    MAIL_FROM: EmailStr = Field(..., env="MAIL_FROM")
    MAIL_FROM_NAME: str = Field("Fit App", env="MAIL_FROM_NAME")
    MAIL_PORT: int = Field(587, env="MAIL_PORT")
    MAIL_SERVER: str = Field(..., env="MAIL_SERVER")
    MAIL_STARTTLS: bool = Field(True, env="MAIL_STARTTLS")
    MAIL_SSL_TLS: bool = Field(False, env="MAIL_SSL_TLS")
    MAIL_USE_CREDENTIALS: bool = Field(True, env="MAIL_USE_CREDENTIALS")
    MAIL_VALIDATE_CERTS: bool = Field(True, env="MAIL_VALIDATE_CERTS")
    MAIL_SUPPRESS_SEND: bool = Field(False, env="MAIL_SUPPRESS_SEND")
    MAIL_TIMEOUT: int = Field(15, env="MAIL_TIMEOUT")

    # ---------- Infra / Third-party ----------
    REDIS_URL: str = Field("redis://localhost:6379", env="REDIS_URL")

    STRIPE_SECRET_KEY: str = Field(..., env="STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY: str = Field(..., env="STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET: str = Field(..., env="STRIPE_WEBHOOK_SECRET")

    AWS_REGION: str = Field(..., env="AWS_REGION")
    AWS_ACCESS_KEY_ID: str | None = Field(None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str | None = Field(None, env="AWS_SECRET_ACCESS_KEY")
    S3_EXERCISE_CATALOG_BUCKET: str = Field(..., env="S3_EXERCISE_CATALOG_BUCKET")

    FRONTEND_URL: str = Field("http://localhost:3000", env="FRONTEND_URL")

    # ---------- OpenAI ----------
    OPENAI_API_KEY: str | None = Field(None, env="OPENAI_API_KEY")
    OPENAI_ORG_ID: str | None = Field(None, env="OPENAI_ORG_ID")
    OPENAI_PROJECT_ID: str | None = Field(None, env="OPENAI_PROJECT_ID")
    OPENAI_MODEL: str = Field("gpt-4o-mini", env="OPENAI_MODEL")

    # ---------- Supabase (optional helpers) ----------
    SUPABASE_URL: str | None = Field(None, env="SUPABASE_URL")
    SUPABASE_ANON_KEY: str | None = Field(None, env="SUPABASE_ANON_KEY")
    SUPABASE_DB_HOST: str | None = Field(None, env="SUPABASE_DB_HOST")
    SUPABASE_DB_PORT: int | None = Field(None, env="SUPABASE_DB_PORT")
    SUPABASE_DB_NAME: str | None = Field(None, env="SUPABASE_DB_NAME")
    SUPABASE_DB_USER: str | None = Field(None, env="SUPABASE_DB_USER")
    SUPABASE_DB_PASSWORD: str | None = Field(None, env="SUPABASE_DB_PASSWORD")

    # ---------- Logging knobs (NEW) ----------
    # Uvicorn log level supports TRACE/DEBUG/INFO/WARNING/ERROR/CRITICAL
    UVICORN_LOG_LEVEL: str = Field("INFO", env="UVICORN_LOG_LEVEL")
    # Whether to output JSON logs (applies to our handlers)
    LOG_JSON: bool = Field(False, env="LOG_JSON")
    # Send logs to file as well as stdout
    LOG_TO_FILE: bool = Field(False, env="LOG_TO_FILE")
    LOG_FILE: str = Field("app.log", env="LOG_FILE")
    LOG_MAX_BYTES: int = Field(1 * 1024 * 1024, env="LOG_MAX_BYTES")  # 1MB
    LOG_BACKUP_COUNT: int = Field(3, env="LOG_BACKUP_COUNT")
    # Minimum level for our own app loggers (not uvicorn internals)
    APP_LOG_LEVEL: str = Field("INFO", env="APP_LOG_LEVEL")

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
        extra="ignore",
    )

    # -------- LOGGING CONFIG (dictConfig) --------
    @property
    def LOGGING_CONFIG(self) -> dict:
        """
        Returns a dictConfig that:
          - Formats as JSON when LOG_JSON=True, otherwise plain text.
          - Logs to stdout always; to a rotating file when LOG_TO_FILE=True.
          - Configures uvicorn loggers (uvicorn/error/access/asgi).
          - Provides an 'app' logger you can use across your code.
        """
        text_formatter = {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        }
        json_formatter = {
            "()": f"{__name__}.CustomJSONFormatter"
        }

        handlers = {
            "stdout": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "json" if self.LOG_JSON else "text",
            }
        }

        if self.LOG_TO_FILE:
            handlers["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": self.LOG_FILE,
                "maxBytes": self.LOG_MAX_BYTES,
                "backupCount": self.LOG_BACKUP_COUNT,
                "formatter": "json" if self.LOG_JSON else "text",
            }

        handler_names = ["stdout"] + (["file"] if self.LOG_TO_FILE else [])

        # Note: Python logging doesn't natively know TRACE, but Uvicorn does.
        # We set levels as strings—Uvicorn will register TRACE for its loggers.
        uvicorn_level = _upper_or_default(self.UVICORN_LOG_LEVEL, "INFO")
        app_level = _upper_or_default(self.APP_LOG_LEVEL, "INFO")

        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "text": text_formatter,
                "json": json_formatter,
            },
            "handlers": handlers,
            "loggers": {
                # Uvicorn root logger (framework messages)
                "uvicorn": {
                    "handlers": handler_names,
                    "level": uvicorn_level,
                    "propagate": False,  # keep uvicorn logs self-contained
                },
                "uvicorn.error": {
                    "handlers": handler_names,
                    "level": uvicorn_level,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": handler_names,
                    "level": uvicorn_level,
                    "propagate": False,
                },
                "uvicorn.asgi": {
                    "handlers": handler_names,
                    "level": uvicorn_level,
                    "propagate": False,
                },
                # Your app logger — use: logging.getLogger("app")
                "app": {
                    "handlers": handler_names,
                    "level": app_level,
                    "propagate": False,
                },
            },
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
