import logging
import os
import re
from http import HTTPStatus
from typing import Dict

from aiohttp import ClientSession
from aiohttp.abc import Request
from aiohttp.web_response import Response

from src.handlers.common import URI, _auth_service, user_authorization_identifier
from src.services.error import ApiError
from src.singletones import client_session

_GITHUB_REDIRECT_URI = f'{URI}/github_auth/redirect'


async def handle_github_redirect(request: Request) -> Response:
    query = {
        'code': request.url.query['code'],
        'client_id': os.environ['GITHUB_CLIENT_ID'],
        'client_secret': os.environ['GITHUB_CLIENT_SECRET'],
    }
    logging.debug(await _get_github_token(query, client_session))
    logging.debug(
        f'Был получен github access_token для пользователя'
        f' {user_authorization_identifier[request.cookies["github_auth"]]}'
    )
    # далее надо сохранить токен в бд
    return Response(status=HTTPStatus.OK, text='Успех')


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
