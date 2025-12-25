import os
import urllib.parse
from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None

# --- Custom DB URL Logic ---
def get_db_url():
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    dbname = os.getenv("DB_NAME", "postgres")
    
    # Cloud SQL (Production)
    connection_name = os.getenv("CLOUDSQL_CONNECTION_NAME")
    if connection_name:
        # Use the standard Cloud SQL socket path
        socket_path = f"/cloudsql/{connection_name}"
        # URL encode the password safely
        encoded_pass = urllib.parse.quote_plus(password)
        # Construct socket connection string
        return f"postgresql+psycopg2://{user}:{encoded_pass}@/{dbname}?host={socket_path}"

    # Local / TCP (Fallback)
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

SQLALCHEMY_DATABASE_URL = get_db_url()
# ---------------------------

def run_migrations_offline() -> None:
    url = SQLALCHEMY_DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        SQLALCHEMY_DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()