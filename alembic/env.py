from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import text  # Added import

from alembic import context

# Add the project root to sys.path to locate modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '..')))

# Import your models' Base
from db_ops.models import Base  # Adjust the import path as necessary

# this is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# Set target_metadata to your models' Base metadata
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Optional: Compare types during autogenerate
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)

    with connectable.connect() as connection:
        # Enable foreign key constraints for SQLite
        if connection.dialect.name == 'sqlite':
            connection.execute(text("PRAGMA foreign_keys=ON"))  # Modified line

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Optional: Compare types during autogenerate
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
