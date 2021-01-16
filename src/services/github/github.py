import logging
from dataclasses import dataclass
from typing import Any, List

from aiohttp import ClientSession
from psycopg2.errors import UniqueViolation
from pydantic import parse_obj_as

from src import URI
from src.services.github.base import GithubEvent, GithubEventParser, GithubEventType
from src.services.github.factory import get_event_parser
from src.services.user_activity import UserActivity


@dataclass
class GithubUser:
    user_name: str
    access_token: str


async def _get_github_events(
    user_name: str, clientSession: ClientSession, access_token: str
) -> List[GithubEvent]:
    async with clientSession.get(
        f'https://api.github.com/users/{user_name}/events',
        headers={'Authorization': f'token {access_token}'},
    ) as response:
        data = await response.json()
        return parse_obj_as(List[GithubEvent], data)


def _get_event_parsers(
    events: List[GithubEvent], session: ClientSession, access_token: str
) -> List[GithubEventParser]:
    event_parsers: List[GithubEventParser] = []
    for event in events:
        if event.type not in [
            GithubEventType.Push,
            GithubEventType.PullRequestReview,
            GithubEventType.PullRequestReviewComment,
            GithubEventType.IssueComment,
            GithubEventType.Issue,
        ]:
            continue
        event_parsers.append(get_event_parser(event, session, access_token))
    return event_parsers


async def get_github_activity(
    user_name: str, access_token: str, session: ClientSession
) -> List[UserActivity]:
    github_events = await _get_github_events(user_name, session, access_token)
    event_parsers = _get_event_parsers(github_events, session, access_token)
    result = []
    for event_parser in event_parsers:
        result += await event_parser.parse()
    logging.info(f'res: {result}')
    return result


def generate_github_auth_link(user_telegram_id: int) -> str:
    return f'{URI}/github_auth/{user_telegram_id}'


async def _get_github_user(user_id: int, conn: Any) -> GithubUser:
    raw_user = await conn.execute(
        'SELECT * FROM github_user_data where user_id = %s', user_id
    )
    return GithubUser(**await raw_user.fetchone())


async def _save_github_user(
    user_id: int, access_token: str, github_user_name: str, conn: Any
) -> None:
    logging.debug(f'user_id: {user_id}')
    try:
        await conn.execute(
            'INSERT INTO github_user_data (user_id, access_token, user_name) VALUES(%s, %s, %s)',
            user_id,
            access_token,
            github_user_name,
        )
    except UniqueViolation:  # пользователь уже есть, просто перезапишем его данные
        await conn.execute(
            'UPDATE github_user_data SET access_token = %s user_name = %s WHERE user_id = %s',
            access_token,
            github_user_name,
            user_id,
        )
