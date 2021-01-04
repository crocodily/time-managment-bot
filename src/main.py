import asyncio
import logging
from typing import AsyncGenerator

from aiohttp import web
from aiohttp.abc import Application, Request
from aiohttp.web_response import Response
from async_cron.schedule import Scheduler

from src.db import get_db_engine
from src.tasks.handlers import handlers
from src.tasks.task import create_task, recreate_tasks


async def handler_example(request: Request) -> Response:
    await create_task(
        request.app['engine'],
        request.app['scheduler'],
        handlers['test'],
        dict(),
        'every(5).second',
    )
    return Response(text='123', status=200)


async def pg_engine(app: Application) -> AsyncGenerator:
    app['engine'] = await get_db_engine()
    await recreate_tasks(app['engine'], app['scheduler'])
    yield
    await app['engine'].close()


async def start_api(app: Application):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()


def main():
    logging.info('App startup')
    loop = asyncio.get_event_loop()
    app = web.Application()
    app['scheduler'] = Scheduler()
    app.add_routes([web.get('/', handler_example)])
    app.cleanup_ctx.append(pg_engine)
    loop.run_until_complete(start_api(app))
    loop.run_until_complete(app['scheduler'].start())


if __name__ == '__main__':
    main()
