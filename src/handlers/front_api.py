from datetime import date

import aiohttp_jinja2
from aiohttp import web
from aiohttp.abc import Request
from aiohttp.web_response import Response

from src.services.common import get_user_activities_by_date
from src.singletones import engine


async def get_user_activity(request: Request) -> Response:
    user_id = int(request.match_info['user_id'])
    today = date.today()
    async with engine.acquire() as conn:
        response = {
            'activities': [activity.to_dict() for activity in
                           await get_user_activities_by_date(
                               user_id=user_id, conn=conn,
                               activity_date=today
                           )],
            'date': today.strftime('%Y-%m-%dZ')
        }
    return web.json_response(response)


@aiohttp_jinja2.template('index.html')
async def get_report_page(request: Request) -> Response:
    return {'request': request}
