import logging
from dataclasses import dataclass
from typing import Any, Optional, cast

from src.db import user_account


@dataclass
class User:
    id: int
    telegram_id: int
    timezone: str
    working_day_start_at: str
    working_day_finish_at: str


async def _create_user(telegram_id: int, conn: Any) -> None:
    await conn.execute(
        'INSERT INTO user_account (telegram_id) VALUES(%s);', telegram_id
    )


async def get_user_by_telegram_id(telegram_id: int, conn: Any) -> Optional[User]:
    raw_result = await conn.execute(
        user_account.select().where(user_account.c.telegram_id == telegram_id)
    )
    result = await raw_result.fetchone()
    if result:
        return User(**result)
    return None


async def create_user_if_not_exists(telegram_id: int, conn: Any) -> int:
    user = await get_user_by_telegram_id(telegram_id, conn)
    if user:
        return user.id
    await _create_user(telegram_id, conn)
    user = await get_user_by_telegram_id(telegram_id, conn)
    user = cast(User, user)
    logging.debug(f'В бд добавлен пользователь с telegram_id: {telegram_id}')
    return user.id


async def save_user_day_start_time(
    telegram_id: int, day_starts_at: str, conn: Any
) -> None:
    await conn.execute(
        'UPDATE user_account SET working_day_start_at=%s where telegram_id = %s',
        day_starts_at,
        telegram_id,
    )
    logging.debug(
        f'Было сохранено время начала рабочего дня для пользователя telegram_id: {telegram_id}'
    )


async def save_user_day_end_time(telegram_id: int, day_ends_at: str, conn: Any) -> None:
    await conn.execute(
        'UPDATE user_account SET working_day_finish_at=%s where telegram_id = %s',
        day_ends_at,
        telegram_id,
    )
    logging.debug(
        f'Было сохранено время конца рабочего дня для пользователя telegram_id: {telegram_id}'
    )
