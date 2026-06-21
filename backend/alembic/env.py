from logging.config import fileConfig

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import engine_from_config, pool
from alembic import context

from app.core.config import settings
from app.models.base import Base
from app.models.user import User  # noqa: F401 确保模型被导入
from app.models.h5_user import H5User  # noqa: F401
from app.models.department import Department  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.menu import Menu  # noqa: F401

config = context.config
# Alembic 使用同步驱动，将 aiomysql 替换为 pymysql
sync_url = settings.DATABASE_URL.replace("mysql+aiomysql", "mysql+pymysql")
config.set_main_option("sqlalchemy.url", sync_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()