"""Application settings and YAML configuration loading."""

from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.exceptions import ConfigurationError

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime configuration sourced from environment variables and .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "LLM Gateway & Foundation Model Hosting Platform"
    environment: Literal["development", "test", "production"] = "development"
    api_version: str = "v1"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    prompt_logging_enabled: bool = False

    api_key_header: str = "X-API-Key"
    llm_gateway_api_key: str = "dev-api-key"
    admin_api_key: str = "dev-admin-key"
    cors_allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    max_request_bytes: int = 1_000_000

    redis_url: str = "redis://localhost:6379/0"
    redis_required: bool = False
    cache_ttl_seconds: int = 300
    in_memory_cache_enabled: bool = True

    database_url: str = "sqlite+aiosqlite:///./llm_gateway.db"
    rag_enabled: bool = True
    vector_store_path: str = "./data/vector_store"
    prefer_mock_provider: bool = True
    embedding_model_id: str = "sentence-transformers/all-MiniLM-L6-v2"

    models_config_path: Path = BASE_DIR / "configs" / "models.yaml"
    routing_config_path: Path = BASE_DIR / "configs" / "routing.yaml"
    policies_config_path: Path = BASE_DIR / "configs" / "policies.yaml"

    request_timeout_seconds: float = 30.0
    provider_timeout_seconds: float = 25.0
    max_concurrent_requests: int = 32
    rate_limit_requests_per_minute: int = 60

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_csv_list(cls, value: Any) -> list[str]:
        """Allow comma-separated env vars for list settings."""
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def allowed_api_keys(self) -> set[str]:
        return {self.llm_gateway_api_key, self.admin_api_key}


def load_yaml_file(path: Path) -> dict[str, Any]:
    """Load a YAML file into a dictionary."""
    if not path.exists():
        raise ConfigurationError(f"Missing configuration file: {path}")

    with path.open("r", encoding="utf-8") as file:
        loaded = yaml.safe_load(file) or {}

    if not isinstance(loaded, dict):
        raise ConfigurationError(f"Configuration file must contain a mapping: {path}")
    return loaded


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
