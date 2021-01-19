import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional, cast, List

from aiopg.sa import Engine

from src.db import user_account, user_activity
from src.handlers.vk import VkUser
from src.services.github.github import GithubUser, get_github_activity
from src.services.user_activity import UserActivity
from src.singletones import engine, client_session, bot
from src.telebot.bot import send_report_message


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


async def save_user_activities(user_id: int, conn: Any) -> None:
    activities = await _get_user_activities(user_id, conn)
    # aiopg не умеет bulk_insert https://github.com/aio-libs/aiopg/issues/112
    for activity in activities:
        await conn.execute(user_activity.insert().values(
            user_id=user_id, service_name=activity.service_name,
            description=activity.description, from_time=activity.from_time,
            to_time=activity.to_time
        ))


async def get_user(conn: Any, user_id: Optional[int] = None, telegram_id: Optional[int] = None,
                   raise_if_empty: bool = False) -> Optional[User]:
    if not user_id and not telegram_id:
        raise RuntimeError('Не передан `user_id` или `telegram_id`')
    if user_id and telegram_id:
        raise RuntimeError('Переданы и `user_id` и `telegram_id`')
    query = user_account.select()
    if telegram_id:
        query = query.where(user_account.c.telegram_id == telegram_id)
    else:
        query = query.where(user_account.c.id == user_id)
    raw_result = await conn.execute(query)
    result = await raw_result.fetchone()
    if result:
        return User(**result)
    if raise_if_empty:
        raise RuntimeError(f'User {user_id or telegram_id} not found')
    return None


async def create_user_if_not_exists(telegram_id: int, conn: Any) -> int:
    user = await get_user(telegram_id=telegram_id, conn=conn)
    if user:
        return user.id
    await _create_user(telegram_id, conn)
    user = await get_user(telegram_id=telegram_id, conn=conn)
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


@dataclass
class UserServices:
    user_id: int
    vk: Optional[VkUser] = None
    github: Optional[GithubUser] = None


async def _get_user_services(user_id: int, conn: Any) -> UserServices:
    raw_summary = await conn.execute(
        """
    SELECT telegram_id, vk_user_id,
    vk.access_token as vk_access_token,
    github.access_token as github_access_token,
    github.user_name as github_username
    FROM user_account 
    LEFT JOIN vk_user_data vk 
    ON vk.user_id = id 
    LEFT JOIN github_user_data github 
    ON github.user_id = id
    WHERE id = %s
    LIMIT 1;
    """,
        user_id
    )
    summary = await raw_summary.fetchone()
    vk_user = VkUser(access_token=summary.vk_access_token, user_id=summary.vk_user_id) if summary.vk_user_id else None
    github_user = GithubUser(user_name=summary.github_username,
                             access_token=summary.github_access_token) if summary.github_username else None
    return UserServices(
        user_id=user_id,
        vk=vk_user,
        github=github_user
    )


async def _get_user_activities(user_id: int, conn: Any) -> List[UserActivity]:
    user = await get_user(user_id=user_id, conn=conn)
    if not user:
        raise RuntimeError('User not found')
    hours, minutes = user.working_day_start_at.split(':')
    user_services = await _get_user_services(user_id, conn)
    activities: List[UserActivity] = []
    if user_services.vk:
        logging.debug('proccess_vk_activities')
    if user_services.github:
        github = user_services.github
        activities += await get_github_activity(
            github.user_name, github.access_token, client_session,
            datetime.now(timezone.utc).replace(year=1992)
        )
    return activities


async def on_workday_ends(telegram_id: int, db: Engine, **_) -> None:
    async with db.acquire() as conn:
        user = await get_user(conn=conn, telegram_id=telegram_id, raise_if_empty=True)
        user = cast(User, user)
        await save_user_activities(user.id, conn)

    await send_report_message(bot, user_id=user.id, telegram_id=telegram_id)
