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

cron_task = sa.Table(
    'cron_task',
    _metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255)),
    sa.Column('args', sa.String(255)),
    sa.Column('time_args', sa.String(255)),
)

user_account = sa.Table(
    'user_account',
    _metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('telegram_id', sa.Integer()),
    sa.Column('timezone', sa.String(70)),
    sa.Column('working_day_start_at', sa.String(70)),
    sa.Column('working_day_finish_at', sa.String(70)),
)

# Если нужно будет написать какой-то сложный запрос и не хочется писать вручную,
# то можно создать вот такую переменную и с помощью алхимии сконструировать запрос

_tables_create_sql: List[str] = [
    """
    CREATE TABLE cron_task (
        id serial PRIMARY KEY NOT NULL,
        name varchar(50) NOT NULL ,
        args varchar(250) NOT NULL,
        time_args varchar(250) NOT NULL
        );
    """,
    # последние три поля переделать в другойт ип данных, когда буду ближе работать со временем
    """
    CREATE TABLE user_account (
        id serial PRIMARY KEY NOT NULL,
        telegram_id INT NOT NULL UNIQUE,
        timezone varchar(70),
        working_day_start_at varchar(70),
        working_day_finish_at varchar(70)
    );
    """,
    """
    CREATE TABLE vk_user_data (
        user_id INT NOT NULL REFERENCES user_account(id) UNIQUE,
        access_token varchar(100) NOT NULL,
        vk_user_id varchar(50) NOT NULL
    );
    """,
    """ 
    CREATE TABLE github_user_data (
        user_id INT NOT NULL REFERENCES user_account(id) UNIQUE,
        access_token varchar(100) NOT NULL,
        user_name varchar(50)
    );
    """,
]


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
