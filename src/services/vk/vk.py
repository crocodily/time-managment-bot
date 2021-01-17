import logging
from dataclasses import dataclass
from http import HTTPStatus
from random import randint
from typing import Any, Dict, List

from aiohttp import ClientSession
from aiopg.sa import Engine

from src import URI
from src.services.error import ApiError
from src.services.user_activity import UserActivity


@dataclass
class VKUser:
    id: str
    vk_id: str
    access_token: str


def generate_vk_auth_link(user_telegram_id: int) -> str:
    return f'{URI}/vk_auth/{user_telegram_id}'


def _construct_query(vk_users: List[VKUser]) -> Dict:
    user_ids: List[str] = list(map(lambda user: user.vk_id, vk_users))
    user_to_use_access_token = randint(0, len(vk_users) - 1)
    fields = 'online, last_seen'
    access_token = vk_users[user_to_use_access_token].access_token
    vk_api_version = '5.126'
    return {
        'user_ids': user_ids,
        'fields': fields,
        'access_token': access_token,
        'v': vk_api_version,
    }


async def _get_users(db: Engine) -> List[VKUser]:
    return [
        VKUser(
            '1',
            '124205288',
            '117d5986ef09b251b50eeb14a27c2e58c33fa5611559ad04eeedebfabd113c2f3b3cf17b288d1fe228cb2',
        )
    ]


def get_vk_activity() -> List[UserActivity]:
    # сходить в базу, считать вершины за последний день(имеенно для этого пользователя)

    pass


# пример ответа
'''
{
"response": [{
"id": 210700286,
"first_name": "Lindsey",
"last_name": "Stirling",
"is_closed": false,
"can_access_closed": true,
"photo_50": "https://sun9-39.u...gaEKflurs&ava=1",
"verified": 1
}]
}
'''


async def get_users_online_status(db: Engine, session: ClientSession, **_: Any) -> None:
    # FIXME: кол-во пользователей в query - не больше 1000, сейчас не критично, потом править
    query = _construct_query(await _get_users(db))
    async with session.get(
            'https://api.vk.com/method/users.get', params=query
    ) as response:
        if response.status != HTTPStatus.OK:
            raise ApiError(
                'Произошла попытка при обращении к api VK', error=await response.text()
            )
        logging.info(f'res {await response.json()}')
    # записываем для каждого пользователя новые веришны в бд
