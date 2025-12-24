from __future__ import annotations

import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    env: str = os.getenv("ENV", "local")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    project_name: str = os.getenv("PROJECT_NAME", "Starter Project")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    port: int = int(os.getenv("PORT", "8000"))
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "starter-project")
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "5"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    db_pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    db_statement_timeout_ms: int = int(os.getenv("DB_STATEMENT_TIMEOUT_MS", "0"))
    allow_origins: str = os.getenv("ALLOW_ORIGINS", "*")
    db_socket_dir: str = os.getenv("DB_SOCKET_DIR", "/cloudsql")
    cloudsql_connection_name: str = os.getenv("CLOUDSQL_CONNECTION_NAME", "")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
