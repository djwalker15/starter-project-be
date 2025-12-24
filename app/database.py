# app/database.py
from __future__ import annotations

import urllib.parse
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings

settings = get_settings()

def _build_async_db_url() -> str:
    user = settings.db_user
    pwd_raw = settings.db_password
    dbname = settings.db_name
    host = settings.db_host
    port = settings.db_port
    socket_dir = settings.db_socket_dir
    conn_name = settings.cloudsql_connection_name
    env = settings.env

    if not user or not pwd_raw or not dbname:
        raise RuntimeError("DB_USER, DB_PASSWORD, and DB_NAME must be set.")

    # URL-encode password
    pwd = urllib.parse.quote_plus(pwd_raw)

    # 1. Cloud SQL via Unix Socket (Production)
    if socket_dir and conn_name:
        # asyncpg connects via directory, not "host=..." query param for unix sockets usually,
        # but SQLAlchemy handling varies.
        # Common pattern: postgresql+asyncpg://user:pass@/dbname?host=/cloudsql/INSTANCE
        query = urllib.parse.urlencode({"host": f"{socket_dir.rstrip('/')}/{conn_name}"})
        return f"postgresql+asyncpg://{user}:{pwd}@/{dbname}?{query}"

    # 2. TCP Connection (Local/Dev)
    return f"postgresql+asyncpg://{user}:{pwd}@{host}:{port}/{dbname}"


# ---------------
# Engine & Session
# ---------------

_ASYNC_ENGINE: AsyncEngine | None = None
_AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


def get_async_engine() -> AsyncEngine:
    global _ASYNC_ENGINE, _AsyncSessionLocal
    if _ASYNC_ENGINE is None:
        url = _build_async_db_url()
        _ASYNC_ENGINE = create_async_engine(
            url,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout,
            pool_pre_ping=True,
            echo=(settings.env == "local"),
        )
        _AsyncSessionLocal = async_sessionmaker(
            bind=_ASYNC_ENGINE,
            autoflush=False,
            expire_on_commit=False,
            future=True,
        )
    return _ASYNC_ENGINE


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for DB session."""
    get_async_engine()  # Ensure initialized
    assert _AsyncSessionLocal is not None
    async with _AsyncSessionLocal() as session:
        yield session


# -------------
# Health checks
# -------------

async def ping() -> bool:
    """Lightweight connectivity check."""
    engine = get_async_engine()
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False