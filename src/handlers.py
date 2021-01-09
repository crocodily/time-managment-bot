import logging
import os
from http import HTTPStatus

from aiohttp import ClientSession
from aiohttp.abc import Request
from aiohttp.web_response import Response

from src.services.error import ApiError
from src.tasks.handlers import handlers
from src.tasks.task import create_task


# пример использования
async def handler_example(request: Request) -> Response:
    await create_task(
        db=request.app['engine'],
        scheduler=request.app['scheduler'],
        function=handlers['test'],
        args=dict(
            user_name='nesb1',
            access_token='8a9c47d43ed9259eaa170773714b052334b56a53',
        ),
        time_args='every(5).second',
        session=request.app['session'],
    )
    return Response(text='123', status=200)


async def handle_github_redirect(request: Request) -> Response:
    session: ClientSession = request.app['session']
    query = {
        'code': request.url.query['code'],
        'client_id': os.environ['GITHUB_CLIENT_ID'],
        'client_secret': os.environ['GITHUB_CLIENT_SECRET'],
    }

    async with session.post(
        'https://github.com/login/oauth/access_token', params=query
    ) as response:
        if response.status != HTTPStatus.OK:
            raise ApiError(
                'Произошла ошибка при попытке получить github access_token',
                await response.text(),
            )
    return Response(status=HTTPStatus.NO_CONTENT)


async def handle_vk_redirect(request: Request) -> Response:
    query_params = {
        'client_id': os.environ['VK_CLIENT_ID'],
        'client_secret': os.environ['VK_CLIENT_SECRET'],
        'redirect_uri': f'{os.environ["HOST"]}/vk_auth',
        'code': request.query['code'],
    }
    session: ClientSession = request.app['session']
    async with session.get(
        'https://oauth.vk.com/access_token', params=query_params
    ) as response:
        if response.status != HTTPStatus.OK:
            raise ApiError(
                'Произошла ошибка при попытке поулчить vk access_token',
                await response.text(),
            )
        logging.info(await response.json())
    return Response(
        status=HTTPStatus.OK,
        text='Авторизация успешно выполнена, можете вернуться обратно в telegram',
    )
