import asyncio
import logging
from typing import AsyncGenerator, Callable

import aiohttp
from aiohttp import ClientSession, web
from aiohttp.abc import Application, Request
from aiohttp.web_middlewares import middleware
from aiohttp.web_response import Response
from async_cron.schedule import Scheduler

from src.db import get_db_engine
from src.handlers import handle_github_redirect, handler_example
from src.tasks.task import recreate_tasks


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


async def start_api(app: Application):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()


@middleware
async def error_handler_middleware(request: Request, handler: Callable):
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
        [web.get('/', handler_example), web.get('/github_auth', handle_github_redirect)]
    )
    app.cleanup_ctx.append(session)
    app.cleanup_ctx.append(pg_engine)
    loop.run_until_complete(start_api(app))
    loop.run_until_complete(app['scheduler'].start())


if __name__ == '__main__':
    main()
