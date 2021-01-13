import asyncio
import logging
from typing import Callable

from aiohttp import web
from aiohttp.abc import Application, Request
from aiohttp.web_middlewares import middleware
from aiohttp.web_response import Response

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
    app.add_routes(
        [
            web.get('/vk_auth/redirect', handle_vk_redirect),
            web.get('/github_auth/redirect', handle_github_redirect),
            web.get('/vk_auth/{telegram_id}', auth_vk),
            web.get('/github_auth/{telegram_id}', auth_github),
        ]
    )
    loop.run_until_complete(start_api(app))
    loop.run_until_complete(init_dispatcher(dp))
    asyncio.ensure_future(dp.start_polling(), loop=loop)
    asyncio.ensure_future(scheduler.start())
    logging.info('Ready to accept connections')

    try:
        loop.run_forever()

    except KeyboardInterrupt:
        logging.info('KeyboardInterrupt')
        loop.run_until_complete(shutdown())
        loop.stop()

    loop.close()

    logging.info('Application stopped')


if __name__ == '__main__':
    main()
