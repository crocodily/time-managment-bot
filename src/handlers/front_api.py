import logging
from datetime import datetime, tzinfo
from typing import List

import aiohttp_jinja2
from aiohttp import web
from aiohttp.abc import Request
from aiohttp.web_response import Response

from src.services.github.github import get_github_activity
from src.services.user_activity import UserActivity
from src.singletones import client_session, engine


async def _get_real_activities(user_id: int) -> List[UserActivity]:
    async with engine.acquire() as conn:
        raw_summary = await conn.execute(
            """
        SELECT telegram_id, vk_user_id,
        vk.access_token as vk_access_token,
        github.access_token as github_access_token,
        github.user_name as github_username
        from user_account 
        left join vk_user_data vk 
        on vk.user_id = id 
        left join github_user_data github 
        on github.user_id = id
        where id = %s
        limit 1;
        """,
            user_id,
        )
        activities: List[UserActivity] = []
        summary = await raw_summary.fetchone()
        if summary.vk_user_id:
            logging.debug('proccess_vk_activities')
        if summary.github_username:
            activities += await get_github_activity(
                summary.github_username, summary.github_access_token, client_session
            )
        return activities


def _get_fake_activity() -> List[UserActivity]:
    format = '%Y:%m:%d:%H:%M'
    return [
        UserActivity(
            'github', 'commit',
            datetime.strptime('2021:1:16:10:00', format),
            datetime.strptime('2021:1:16:12:00', format)
        )
    ]


async def get_user_activity(request: Request) -> Response:
    user_id = request.match_info['user_id']
    response = {
        'activities': [activity.to_dict() for activity in _get_fake_activity()],
        'date': str(datetime.strptime('2021:1:16:10:00', '%Y:%m:%d:%H:%M'))
    }
    return web.json_response(response)


@aiohttp_jinja2.template('index.html')
async def get_report_page(request: Request) -> Response:
    return {'request': request}
