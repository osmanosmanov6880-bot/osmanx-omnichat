"""SQLAlchemy migration environment; schema is declared in app.db."""
from logging.config import fileConfig
from pathlib import Path
from dotenv import load_dotenv

# Use the same local configuration for migrations as the API process.
load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)
import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from app.db import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL', config.get_main_option('sqlalchemy.url')).replace('%','%%'))
target_metadata = Base.metadata


def do_migrations_offline():
    context.configure(url=config.get_main_option('sqlalchemy.url'), target_metadata=target_metadata,
                      literal_binds=True, dialect_opts={'paramstyle': 'named'}, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


def do_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section),prefix='sqlalchemy.',poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection,target_metadata=target_metadata,compare_type=True)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    do_migrations_offline()
else:
    do_migrations_online()
