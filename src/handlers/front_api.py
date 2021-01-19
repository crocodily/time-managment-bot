from datetime import datetime
from typing import List

import aiohttp_jinja2
from aiohttp import web
from aiohttp.abc import Request
from aiohttp.web_response import Response

from src.services.user_activity import UserActivity

def _get_fake_activity() -> List[UserActivity]:
    format = '%Y-%m-%dT%H:%MZ'
    return [
        UserActivity(
            'github', 'review',
            datetime.strptime('2021-1-17T10:30Z', format),
            datetime.strptime('2021-1-17T10:33Z', format)
        ),
        UserActivity(
            'github', 'review',
            datetime.strptime('2021-1-17T10:41Z', format),
            datetime.strptime('2021-1-17T10:44Z', format)
        ),
        UserActivity(
            'github', 'review',
            datetime.strptime('2021-1-17T10:45Z', format),
            datetime.strptime('2021-1-17T10:48Z', format)
        ),
        UserActivity(
            'github', 'review',
            datetime.strptime('2021-1-17T10:51Z', format),
            datetime.strptime('2021-1-17T10:54Z', format),
        ),
        UserActivity(
            'github', 'review',
            datetime.strptime('2021-1-17T11:10Z', format),
            datetime.strptime('2021-1-17T11:13Z', format),
        ),
        UserActivity(
            'github', 'review',
            datetime.strptime('2021-1-17T11:18Z', format),
            datetime.strptime('2021-1-17T11:21Z', format),
        ),
        UserActivity(
            'github', 'review',
            datetime.strptime('2021-1-17T11:34Z', format),
            datetime.strptime('2021-1-17T11:37Z', format),
        ),
        UserActivity(
            'github', 'commit',
            datetime.strptime('2021-1-17T14:00Z', format),
            datetime.strptime('2021-1-17T14:03Z', format),
        ),
        UserActivity(
            'github', 'commit',
            datetime.strptime('2021-1-17T16:15Z', format),
            datetime.strptime('2021-1-17T16:18Z', format),
        ),
        UserActivity(
            'github', 'commit',
            datetime.strptime('2021-1-17T17:50Z', format),
            datetime.strptime('2021-1-17T17:53Z', format),
        ),
        UserActivity(
            'vk', 'online',
            datetime.strptime('2021-1-17T11:00Z', format),
            datetime.strptime('2021-1-17T11:45Z', format),
        ),
        UserActivity(
            'vk', 'online',
            datetime.strptime('2021-1-17T15:00Z', format),
            datetime.strptime('2021-1-17T15:25Z', format),
        ),
        UserActivity(
            'vk', 'online',
            datetime.strptime('2021-1-17T17:50Z', format),
            datetime.strptime('2021-1-17T18:00Z', format),
        ),

    ]

async def get_user_activity(request: Request) -> Response:
    user_id = request.match_info['user_id']
    response = {
        'activities': [activity.to_dict() for activity in _get_fake_activity()],
        'date': datetime.strptime('2021-1-17:10Z', '%Y-%m-%d%H:%MZ').strftime('%Y-%m-%dT%H:%MZ')
    }
    return web.json_response(response)


@aiohttp_jinja2.template('index.html')
async def get_report_page(request: Request) -> Response:
    return {'request': request}
