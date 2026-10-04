"""
Cortex Engineering — Alembic Environment Configuration.

Configures Alembic to use the application's database URL and
SQLAlchemy metadata for auto-generating migrations.
"""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Add the backend directory to the Python path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.base import Base  # noqa: E402
from app.models import *  # noqa: E402, F401, F403 — import all models for metadata

# Alembic Config object
config = context.config

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for auto-generation
target_metadata = Base.metadata

# Override the sqlalchemy.url from environment variable if available
database_url = os.environ.get("DATABASE_URL_SYNC")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode — generates SQL script without
    connecting to the database.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode — connects to the database
    and applies migrations directly.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
