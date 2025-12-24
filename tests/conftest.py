import random
import socket as _socket
import sys
import time
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure 'app' is importable in CI without package install
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import get_db
from app.main import app
from app.models import Base


@pytest.fixture(autouse=True)
def _hermetic_env(monkeypatch):
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("APP_NAME", "fastapi-starter-test")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    monkeypatch.setenv("TZ", "UTC")
    if hasattr(time, "tzset"):
        time.tzset()
    random.seed(1337)


@pytest.fixture(autouse=True)
def _block_network(monkeypatch):
    """
    Block real network (AF_INET/AF_INET6) but allow AF_UNIX for asyncio's self-pipe.
    This is hermetic and independent of pytest-socket APIs.
    """
    real_socket = _socket.socket
    allowed_families = {_socket.AF_UNIX}

    def guarded_socket(family=_socket.AF_INET, type=_socket.SOCK_STREAM, proto=0, fileno=None):
        # Allow sockets created from a file descriptor (fileno) to avoid breaking internals
        if fileno is None and family not in allowed_families:
            raise RuntimeError("Network calls are disabled during tests")
        return real_socket(family, type, proto, fileno)

    monkeypatch.setattr(_socket, "socket", guarded_socket)
    yield


@pytest.fixture(scope="session")
def engine():
    # Allow the same in-memory SQLite DB connection to be used across threads
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
    )
    with engine.begin() as conn:
        Base.metadata.create_all(conn)
    return engine


@pytest.fixture
def db_session(engine):
    # Single connection + transaction per test, safe across threads due to check_same_thread=False
    connection = engine.connect()
    trans = connection.begin()
    TestSession = sessionmaker(
        bind=connection,
        autoflush=False,
        autocommit=False,
        future=True,
        expire_on_commit=False,
    )
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        trans.rollback()
        connection.close()


@pytest.fixture(autouse=True)
def _override_db_dependency(db_session):
    def _get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def anyio_backend():
    # anyio’s plugin will use this when present
    return "asyncio"


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
