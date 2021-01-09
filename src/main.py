import asyncio
import logging
import os
from typing import AsyncGenerator, Callable

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiohttp import ClientSession, web
from aiohttp.abc import Application, Request
from aiohttp.web_middlewares import middleware
from aiohttp.web_response import Response
from async_cron.schedule import Scheduler

from src.db import get_db_engine
from src.handlers import handle_github_redirect, handle_vk_redirect, handler_example
from src.tasks.task import recreate_tasks
from src.telebot.handler import init_dispatcher


async def session(app: Application) -> AsyncGenerator:
    jar = aiohttp.CookieJar(unsafe=True, quote_cookie=False)
    app['session'] = ClientSession(cookie_jar=jar)
    yield
    await app['session'].close()


async def pg_engine(app: Application) -> AsyncGenerator:
    app['engine'] = await get_db_engine()
    await recreate_tasks(app['engine'], app['scheduler'], app['session'])
    yield
    await app['engine'].close()


async def bot(app: Application) -> AsyncGenerator:
    app['bot'] = Bot(token=os.environ['BOT_TOKEN'])
    yield
    # This method's behavior will be changed in aiogram v3.0
    # сейчас `close` закрывает aiohttp.ClientSession
    await app['bot'].close()


async def start_api(app: Application) -> None:
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 80)
    await site.start()


@middleware
async def error_handler_middleware(request: Request, handler: Callable) -> Response:
    try:
        return await handler(request)
    except Exception as err:  # pylint: disable=W0703
        logging.exception('Unhandled error:')
        return Response(status=500, text=f'Unhandled error: {str(err)}')


def main():
    logging.info('App startup')
    loop = asyncio.get_event_loop()
    app = web.Application()
    app['scheduler'] = Scheduler()
    app.add_routes(
        [
            web.get('/', handler_example),
            web.get('/github_auth', handle_github_redirect),
            web.get('/vk_auth', handle_vk_redirect),
        ]
    )
    app.cleanup_ctx.append(session)
    app.cleanup_ctx.append(pg_engine)
    app.cleanup_ctx.append(bot)
    loop.run_until_complete(start_api(app))
    storage = MemoryStorage()
    dp = Dispatcher(app['bot'], loop=loop, storage=storage)
    loop.run_until_complete(init_dispatcher(dp))
    asyncio.ensure_future(dp.start_polling(), loop=loop)
    asyncio.ensure_future(app['scheduler'].start())
    logging.info('Ready to accept connections')

    try:
        loop.run_forever()

    except KeyboardInterrupt:
        logging.info('KeyboardInterrupt')
        loop.stop()

    loop.close()

    logging.info('Application stopped')


if __name__ == '__main__':
    main()
