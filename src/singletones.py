import asyncio
import os

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiohttp import ClientSession
from aiopg.sa import Engine
from async_cron.schedule import Scheduler

from src.db import get_db_engine
from src.tasks.task import recreate_tasks

jar = aiohttp.CookieJar(unsafe=True, quote_cookie=False)
client_session: ClientSession = ClientSession(cookie_jar=jar)
scheduler = Scheduler()
_loop = asyncio.get_event_loop()
engine: Engine = _loop.run_until_complete(get_db_engine())
_loop.run_until_complete(
    recreate_tasks(db=engine, scheduler=scheduler, session=client_session)
)
bot = Bot(token=os.environ['BOT_TOKEN'])
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
