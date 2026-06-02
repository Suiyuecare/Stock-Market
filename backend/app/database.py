from collections.abc import Iterator

from psycopg_pool import ConnectionPool
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings


def _pool_url() -> str:
    return get_settings().database_url.replace("postgresql+psycopg://", "postgresql://")


pool = ConnectionPool(conninfo=_pool_url(), open=False)
engine = create_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_connection() -> Iterator:
    if pool.closed:
        pool.open()

    with pool.connection() as connection:
        yield connection


def get_session() -> Iterator:
    with SessionLocal() as session:
        yield session
