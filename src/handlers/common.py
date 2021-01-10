import os
from typing import Dict
from uuid import uuid4

from aiohttp import web

# со временем нужно убрать это в базу, препятствует запуску
# нескольких инстансов и приводит к утечке памяти
user_authorization_identifier: Dict[str, str] = {}


def _auth_service(user_id: str, redirect_url: str, cookie_name: str) -> None:
    uuid = str(uuid4())
    user_authorization_identifier[uuid] = user_id
    raise web.HTTPFound(redirect_url, headers={'Set-Cookie': f'{cookie_name}={uuid}'})


HOST = os.environ['HOST']
PROTOCOL = os.environ['HOST_PROTOCOL']
URI = f'{PROTOCOL}://{HOST}'
