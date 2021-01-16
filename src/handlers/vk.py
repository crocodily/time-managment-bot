import logging
import os
from http import HTTPStatus
from typing import Dict

from aiohttp import ClientSession
from aiohttp.abc import Request
from aiohttp.web_response import Response
from pydantic import BaseModel

from src import URI
from src.handlers.common import _auth_service, user_authorization_identifier
from src.services.error import ApiError
from src.singletones import client_session

_VK_REDIRECT_URI = f'{URI}/vk_auth/redirect'


async def handle_vk_redirect(request: Request) -> Response:
    logging.debug(f'request {request.query}')
    query_params = {
        'client_id': os.environ['VK_CLIENT_ID'],
        'client_secret': os.environ['VK_CLIENT_SECRET'],
        'redirect_uri': _VK_REDIRECT_URI,
        'code': request.query['code'],
    }
    session: ClientSession = client_session
    await _get_user_data(query_params, session)
    vk_auth_uuid = request.cookies['vk_auth']
    user_id = user_authorization_identifier[vk_auth_uuid]
    logging.info(f'user_id: {user_id}')
    # далее надо сохранить данные в бд
    return Response(
        status=HTTPStatus.OK,
        text='Авторизация успешно выполнена, можете вернуться обратно в telegram',
    )


class VkUser(BaseModel):
    access_token: str
    user_id: str


async def _get_user_data(
    query_params: Dict[str, str], session: ClientSession
) -> VkUser:
    async with session.get(
        'https://oauth.vk.com/access_token', params=query_params
    ) as response:
        if response.status != HTTPStatus.OK:
            raise ApiError(
                'Произошла ошибка при попытке поулчить vk access_token',
                await response.text(),
            )
        vk_user = await response.json()
    return VkUser.parse_obj(vk_user)


def _construct_vk_query() -> str:
    return (
        f'https://oauth.vk.com/authorize?client_id={os.environ["VK_CLIENT_ID"]}'
        f'&redirect_uri={_VK_REDIRECT_URI}'
        '&scope=offline&response_type=code&display=page'
    )


async def auth_vk(request: Request) -> None:
    user_id = request.match_info['telegram_id']
    redirect_url = _construct_vk_query()
    _auth_service(user_id, redirect_url, 'vk_auth')
    # ответ не нужен, так как будет спровоцированно исключение
