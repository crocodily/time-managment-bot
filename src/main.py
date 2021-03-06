import asyncio
import logging
from typing import Callable

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp.abc import Application, Request
from aiohttp.web_middlewares import middleware
from aiohttp.web_response import Response

from src.handlers.front_api import get_report_page, get_user_activity
from src.handlers.github import auth_github, handle_github_redirect
from src.handlers.vk import auth_vk, handle_vk_redirect
from src.singletones import bot, client_session, dp, engine, scheduler
from src.telebot.handler import init_dispatcher


async def start_api(app: Application) -> None:
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 80)
    await site.start()


async def shutdown():
    await client_session.close()
    await engine.close()
    # This method's behavior will be changed in aiogram v3.0
    # сейчас `close` закрывает aiohttp.ClientSession
    await bot.close()


@middleware
async def error_handler_middleware(request: Request, handler: Callable) -> Response:
    try:
        return await handler(request)
    except Exception:  # pylint: disable=W0703
        logging.exception('Unhandled error:')
        return Response(status=500, text='Произошла ошибка')


def main():
    logging.info('App startup')
    loop = asyncio.get_event_loop()
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('/src/front/html'))
    app['static_root_url'] = '/src/front/static'
    app.router.add_static('/src/front/static/', path='/src/front/static', name='static')

    app.add_routes(
        [
            web.get('/vk_auth/redirect', handle_vk_redirect),
            web.get('/github_auth/redirect', handle_github_redirect),
            web.get('/vk_auth/{telegram_id}', auth_vk),
            web.get('/github_auth/{telegram_id}', auth_github),
            web.get('/report/{user_id}', get_user_activity),
            web.get('/report_page/{user_id}', get_report_page),
        ]
    )
    loop.run_until_complete(start_api(app))
    loop.run_until_complete(init_dispatcher(dp))
    asyncio.ensure_future(dp.start_polling(), loop=loop)
    asyncio.ensure_future(scheduler.start())
    logging.info('Ready to accept connections')

    try:
        loop.run_forever()

    except BaseException:  # pylint: disable=W0703
        logging.info('shutdown')
        loop.run_until_complete(shutdown())
        loop.stop()

    loop.close()

    logging.info('Application stopped')


if __name__ == '__main__':
    main()
