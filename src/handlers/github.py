import logging
import os
import re
from http import HTTPStatus
from typing import Any, Dict, cast

from aiohttp import ClientSession
from aiohttp.abc import Request
from aiohttp.web_response import Response
from pydantic import BaseModel

from src import URI
from src.handlers.common import _auth_service, user_authorization_identifier
from src.services.common import User, create_user_if_not_exists, get_user_by_telegram_id
from src.services.error import ApiError
from src.services.github.github import _save_github_user
from src.singletones import client_session, engine

_GITHUB_REDIRECT_URI = f'{URI}/github_auth/redirect'


async def handle_github_redirect(request: Request) -> Response:
    query = {
        'code': request.url.query['code'],
        'client_id': os.environ['GITHUB_CLIENT_ID'],
        'client_secret': os.environ['GITHUB_CLIENT_SECRET'],
    }
    session = client_session
    access_token = await _get_github_token(query, session)
    async with engine.acquire() as conn:
        telegram_id = int(user_authorization_identifier[request.cookies['github_auth']])
    user_name = await _get_github_user_name(access_token, session)
    await _save_github_data(telegram_id, access_token, user_name, conn)
    user = cast(User, await get_user_by_telegram_id(telegram_id, conn))
    logging.debug(f'Был получен github access_token для пользователя' f' {telegram_id}')
    return Response(status=HTTPStatus.OK, text='Авторизация успешно выполнена, можете вернуться обратно в telegram')


class GithubUser(BaseModel):
    login: str


async def _get_github_user_name(access_token: str, session: ClientSession) -> str:
    url = 'https://api.github.com/user'
    async with session.get(
        url, headers={'Authorization': f'token {access_token}'}
    ) as response:
        if response.status != HTTPStatus.OK:
            raise ApiError(
                f'Произошла ошибка при попытке запроса {url}',
                error=await response.text(),
            )
        github_user = GithubUser.parse_obj(await response.json())
    return github_user.login


async def _save_github_data(
    telegram_id: int, access_token: str, github_user_name: str, conn: Any
) -> None:
    user_id = await create_user_if_not_exists(telegram_id, conn)
    await _save_github_user(user_id, access_token, github_user_name, conn)


async def _get_github_token(query: Dict[str, str], session: ClientSession) -> str:
    async with session.post(
        'https://github.com/login/oauth/access_token', params=query
    ) as response:
        if response.status != HTTPStatus.OK:
            raise ApiError(
                'Произошла ошибка при попытке получить github access_token',
                await response.text(),
            )
        text = await response.text()
    res = re.search(r'access_token=(?P<token>\w+)&', text)
    if res:
        return res.groupdict()['token']
    # ответ приходит в таком виде
    # "access_token=8f2080a990c203c0fa9c6da979d6521511d791e9&scope=&token_type=bearer"
    raise RuntimeError(f'Не удалось получить github access_token из ответа {text}')


def _construct_github_query() -> str:
    return (
        'https://github.com/login/oauth/authorize?'
        f'client_id={os.environ["GITHUB_CLIENT_ID"]}'
        f'&redirect_uri={_GITHUB_REDIRECT_URI}'
    )


async def auth_github(request: Request) -> None:
    user_id = request.match_info['telegram_id']
    _auth_service(user_id, _construct_github_query(), 'github_auth')
    # ответ не нужен, так как будет спровоцированно исключение
