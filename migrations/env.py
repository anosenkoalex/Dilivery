from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 🔧 Импортируй app и db из твоего проекта
from app import app, db

# Alembic Config object
config = context.config

# Настройка логов
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 👇 Подставляем URL из Flask-конфига
url = app.config["SQLALCHEMY_DATABASE_URI"]
config.set_main_option("sqlalchemy.url", url)

# 👇 Устанавливаем target_metadata из SQLAlchemy
target_metadata = db.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
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
