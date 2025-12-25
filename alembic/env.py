import os
import urllib.parse
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None

def get_db_url():
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    dbname = os.getenv("DB_NAME", "postgres")
    
    # Cloud SQL (Production)
    connection_name = os.getenv("CLOUDSQL_CONNECTION_NAME")
    if connection_name:
        socket_path = f"/cloudsql/{connection_name}"
        encoded_pass = urllib.parse.quote_plus(password)
        return f"postgresql+psycopg2://{user}:{encoded_pass}@/{dbname}?host={socket_path}"

    # Local / TCP
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

def run_migrations_online() -> None:
    url = get_db_url()
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()