import logging
import os
from asyncio import sleep
from typing import List

import sqlalchemy as sa
from aiopg.sa import Engine, create_engine
from sqlalchemy_utils import create_database, database_exists

db_env = {
    'user': os.environ['PG_USER'],
    'host': os.environ['PG_HOST'],
    'password': os.environ['PG_PASS'],
}
_DATABASE = 'time_management_bot'

_metadata = sa.MetaData()

_tables_create_sql: List[str] = []

cron_task = sa.Table(
    'cron_task',
    _metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255)),
    sa.Column('args', sa.String(255)),
    sa.Column('time_args', sa.String(255)),
)

_tables_create_sql.append(
    """
    CREATE TABLE cron_task (
        id serial PRIMARY KEY,
        name varchar(50),
        args varchar(250),
        time_args varchar(250)
        )
    """
)


async def _create_tables(tables_create_sql: List[str], engine: Engine) -> None:
    async with engine.acquire() as conn:
        for sql in tables_create_sql:
            await conn.execute(sql)


def _make_url(user: str, password: str, host: str, name: str, port: int = 5432) -> str:
    return f'postgresql://{user}:{password}@{host}:{port}/{name}'


async def get_db_engine() -> Engine:
    logging.info('Waiting database startup')
    await sleep(7)
    url = _make_url(port=5432, name=_DATABASE, **db_env)
    new_database: bool = not database_exists(url)
    if new_database:
        create_database(url)

    engine = await create_engine(
        database=_DATABASE,
        **db_env,
    )
    if new_database:
        await _create_tables(tables_create_sql=_tables_create_sql, engine=engine)
    logging.info('Connection with database established')
    return engine
