from collections.abc import Iterator

from psycopg_pool import ConnectionPool

from app.config import get_settings


def _pool_url() -> str:
    return get_settings().database_url.replace("postgresql+psycopg://", "postgresql://")


pool = ConnectionPool(conninfo=_pool_url(), open=False)


def get_connection() -> Iterator:
    if pool.closed:
        pool.open()

    with pool.connection() as connection:
        yield connection
