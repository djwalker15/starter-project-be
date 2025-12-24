# app/db.py
from __future__ import annotations

import urllib.parse
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from app.config import get_settings

# ---------------------------
# Settings & URL construction
# ---------------------------

settings = get_settings()


def _build_db_url_from_parts() -> str | None:
    user = settings.db_user
    pwd_raw = settings.db_password
    dbname = settings.db_name
    host = settings.db_host
    port = settings.db_port
    socket_dir = settings.db_socket_dir
    conn_name = settings.cloudsql_connection_name
    env = settings.env

    if not user or not pwd_raw or not dbname:
        return None

    if env == "local" and host and port:
        pwd = urllib.parse.quote_plus(pwd_raw)
        return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{dbname}"

    if socket_dir and conn_name:
        # postgresql+psycopg2://USER:ENC_PWD@/DBNAME?host=/cloudsql/PROJECT:REGION:INSTANCE
        pwd = urllib.parse.quote_plus(pwd_raw)
        query = urllib.parse.urlencode({"host": f"{socket_dir.rstrip('/')}/{conn_name}"})
        return f"postgresql+psycopg2://{user}:{pwd}@/{dbname}?{query}"

    # if user and pwd_raw and dbname and host and port:
    #     pwd = urllib.parse.quote_plus(pwd_raw)
    #     return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{dbname}"

    # Nothing usable
    return None


def get_database_url() -> str:
    built = _build_db_url_from_parts()
    print(built)
    if built:
        return built
    raise RuntimeError("Database URL not configured.")


# ---------------
# Engine & Session
# ---------------

_ENGINE: Engine | None = None
_SessionLocal: sessionmaker | None = None


def _create_engine() -> Engine:
    url = get_database_url()
    # Pool settings tuned for API usage; adjust as needed
    engine = create_engine(
        url,
        poolclass=QueuePool,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,  # seconds
        pool_pre_ping=True,  # validates connections from pool
        future=True,
    )

    # Optional: set a statement timeout (ms) for all connections
    stmt_timeout_ms = settings.db_statement_timeout_ms
    if stmt_timeout_ms:
        with engine.connect() as conn:
            conn.execute(text(f"SET statement_timeout = {int(stmt_timeout_ms)}"))
            conn.commit()

    return engine


def get_engine() -> Engine:
    global _ENGINE, _SessionLocal
    if _ENGINE is None:
        _ENGINE = _create_engine()
        _SessionLocal = sessionmaker(bind=_ENGINE, autoflush=False, autocommit=False, future=True)
    return _ENGINE


def get_sessionmaker() -> sessionmaker:
    get_engine()  # ensures initialization
    assert _SessionLocal is not None
    return _SessionLocal


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Context-managed session for scripts/background jobs:
        with session_scope() as db:
            ...
    """
    db = get_sessionmaker()()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# -----------------------
# FastAPI dependency hook
# -----------------------


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency:
        @router.get("/items")
        def list_items(db: Session = Depends(get_db)):
            return db.execute(select(Item)).scalars().all()
    """
    db = get_sessionmaker()()
    try:
        yield db
    finally:
        db.close()


# -------------
# Health checks
# -------------


def ping() -> bool:
    """
    Lightweight connectivity check you can call in a health endpoint.
    """
    engine = get_engine()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
