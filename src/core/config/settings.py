"""Application settings loaded from environment variables using pydantic-settings."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configurable values for the service.

    Environment variables can be prefixed with ``DSA_`` (e.g. ``DSA_APP_NAME``).
    """

    app_name: str = Field("DSA AI Coach", description="Human readable application name")
    environment: Literal["development", "staging", "production"] = Field(
        "development",
        description="Deployment environment",
    )
    log_level: str = Field("INFO", description="Logging level for loguru")
    allowed_hosts: list[str] = Field(["*"], description="Hosts allowed by TrustedHostMiddleware")
    cors_origins: list[str] = Field(["*"], description="Allowed origins for CORS middleware")
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[3],
        description="Root directory of the project (computed)",
    )

    # Database Settings
    database_url: str = Field(
        "sqlite+aiosqlite:///./app.db",
        description="Async database connection string",
    )
    database_echo: bool = Field(False, description="SQLAlchemy engine echo mode")
    pool_size: int = Field(5, description="Database pool size")
    max_overflow: int = Field(10, description="Database pool max overflow")

    # JWT Authentication Settings
    jwt_secret_key: str = Field(
        "super-secret-jwt-key-for-development-change-in-production-12345!",
        description="JWT secret key for signing tokens",
    )
    jwt_algorithm: str = Field("HS256", description="JWT signing algorithm")
    access_token_expire_minutes: int = Field(30, description="Access token expiration in minutes")
    refresh_token_expire_days: int = Field(7, description="Refresh token expiration in days")

    # Redis & Cache Settings
    redis_url: str = Field("redis://localhost:6379/0", description="Async Redis connection string")
    redis_max_connections: int = Field(10, description="Maximum connections in Redis pool")
    redis_connect_timeout: float = Field(5.0, description="Redis connection timeout in seconds")
    redis_socket_timeout: float = Field(5.0, description="Redis socket operation timeout in seconds")
    cache_default_ttl: int = Field(3600, description="Default cache TTL in seconds")
    session_ttl: int = Field(86400, description="Default session TTL in seconds (24 hours)")

    # OpenTelemetry & Metrics Settings
    otel_enabled: bool = Field(False, description="Enable OpenTelemetry tracing")
    otel_service_name: str = Field("dsa-ai-coach", description="OpenTelemetry service name")
    otel_exporter_otlp_endpoint: str = Field("http://localhost:4317", description="OTLP exporter endpoint")
    metrics_enabled: bool = Field(True, description="Enable Prometheus metrics collection and route")

    # Background Worker & Queue Settings
    worker_enabled: bool = Field(False, description="Enable async background worker runner")
    worker_max_retries: int = Field(3, description="Max retries for background jobs")
    worker_timeout: int = Field(300, description="Worker job execution timeout in seconds")
    queue_name: str = Field("dsa_job_queue", description="Name of the job queue")
    queue_max_retries: int = Field(3, description="Alias for worker_max_retries")
    queue_job_timeout: int = Field(300, description="Alias for worker_timeout")

    # AI Gateway Settings
    openai_api_key: str = Field("", description="OpenAI API key for AI Gateway")
    nim_api_key: str = Field("", description="NVIDIA NIM API key")
    nim_base_url: str = Field("https://integrate.api.nvidia.com/v1", description="NVIDIA NIM base URL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="DSA_",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("log_level")
    @classmethod
    def _validate_log_level(cls, v: str) -> str:
        allowed = {"TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            msg = "log_level must be a valid logging level"
            raise ValueError(msg)
        return v.upper()

    @property
    def APP_NAME(self) -> str:  # noqa: N802
        """Alias for app_name for backward compatibility."""
        return self.app_name

    @property
    def APP_ENV(self) -> str:  # noqa: N802
        """Alias for environment for backward compatibility."""
        return self.environment

    @property
    def DATABASE_URL(self) -> str:  # noqa: N802
        """Alias for database_url for backward compatibility."""
        return self.database_url

    @property
    def DATABASE_ECHO(self) -> bool:  # noqa: N802
        """Alias for database_echo for backward compatibility."""
        return self.database_echo

    @property
    def POOL_SIZE(self) -> int:  # noqa: N802
        """Alias for pool_size for backward compatibility."""
        return self.pool_size

    @property
    def MAX_OVERFLOW(self) -> int:  # noqa: N802
        """Alias for max_overflow for backward compatibility."""
        return self.max_overflow

    @property
    def JWT_SECRET_KEY(self) -> str:  # noqa: N802
        """Alias for jwt_secret_key for backward compatibility."""
        return self.jwt_secret_key

    @property
    def JWT_ALGORITHM(self) -> str:  # noqa: N802
        """Alias for jwt_algorithm for backward compatibility."""
        return self.jwt_algorithm

    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:  # noqa: N802
        """Alias for access_token_expire_minutes for backward compatibility."""
        return self.access_token_expire_minutes

    @property
    def REFRESH_TOKEN_EXPIRE_DAYS(self) -> int:  # noqa: N802
        """Alias for refresh_token_expire_days for backward compatibility."""
        return self.refresh_token_expire_days

    @property
    def REDIS_URL(self) -> str:  # noqa: N802
        """Alias for redis_url for backward compatibility."""
        return self.redis_url

    @property
    def REDIS_MAX_CONNECTIONS(self) -> int:  # noqa: N802
        """Alias for redis_max_connections for backward compatibility."""
        return self.redis_max_connections

    @property
    def REDIS_CONNECT_TIMEOUT(self) -> float:  # noqa: N802
        """Alias for redis_connect_timeout for backward compatibility."""
        return self.redis_connect_timeout

    @property
    def CACHE_DEFAULT_TTL(self) -> int:  # noqa: N802
        """Alias for cache_default_ttl for backward compatibility."""
        return self.cache_default_ttl

    @property
    def OTEL_ENABLED(self) -> bool:  # noqa: N802
        """Alias for otel_enabled for backward compatibility."""
        return self.otel_enabled

    @property
    def OTEL_SERVICE_NAME(self) -> str:  # noqa: N802
        """Alias for otel_service_name for backward compatibility."""
        return self.otel_service_name

    @property
    def OTEL_EXPORTER_OTLP_ENDPOINT(self) -> str:  # noqa: N802
        """Alias for otel_exporter_otlp_endpoint for backward compatibility."""
        return self.otel_exporter_otlp_endpoint

    @property
    def WORKER_ENABLED(self) -> bool:  # noqa: N802
        """Alias for worker_enabled for backward compatibility."""
        return self.worker_enabled

    @property
    def WORKER_MAX_RETRIES(self) -> int:  # noqa: N802
        """Alias for worker_max_retries for backward compatibility."""
        return self.worker_max_retries

    @property
    def WORKER_TIMEOUT(self) -> int:  # noqa: N802
        """Alias for worker_timeout for backward compatibility."""
        return self.worker_timeout

    @property
    def REDIS_SOCKET_TIMEOUT(self) -> float:  # noqa: N802
        """Alias for redis_socket_timeout."""
        return self.redis_socket_timeout

    @property
    def SESSION_TTL(self) -> int:  # noqa: N802
        """Alias for session_ttl."""
        return self.session_ttl

    @property
    def METRICS_ENABLED(self) -> bool:  # noqa: N802
        """Alias for metrics_enabled."""
        return self.metrics_enabled

    @property
    def QUEUE_NAME(self) -> str:  # noqa: N802
        """Alias for queue_name."""
        return self.queue_name

    @property
    def QUEUE_MAX_RETRIES(self) -> int:  # noqa: N802
        """Alias for queue_max_retries."""
        return self.queue_max_retries

    @property
    def QUEUE_JOB_TIMEOUT(self) -> int:  # noqa: N802
        """Alias for queue_job_timeout."""
        return self.queue_job_timeout


settings = Settings()  # type: ignore[call-arg]
