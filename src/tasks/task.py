import json
from typing import Callable, Dict, List

from aiopg.sa import Engine
from async_cron.job import CronJob
from async_cron.schedule import Scheduler

from src.db import cron_task
from src.tasks.handlers import handlers


async def _insert_task_to_db(
    db: Engine, function_name: str, args: Dict, time_args: str
) -> None:
    async with db.acquire() as conn:
        args_in_json = json.dumps(args)
        await conn.execute(
            cron_task.insert().values(  # pylint: disable=E1120
                name=function_name, args=args_in_json, time_args=time_args
            )
        )


def _start_task(
    scheduler: Scheduler, function: Callable, args: Dict, time_args: str
) -> None:
    job = CronJob(function.__name__)  # type: ignore
    # добавляем аргументы из библиотеки CronJob
    job = eval(f'job.{time_args}')  # pylint: disable=W0123
    job.go(function, **args)
    scheduler.add_job(job)


async def create_task(
    db: Engine, scheduler: Scheduler, function: Callable, args: Dict, time_args: str
) -> None:
    await _insert_task_to_db(db, function.__name__, args, time_args)
    _start_task(scheduler, function, args, time_args)


def _parse_task(task: Dict) -> Dict:
    args = json.loads(task.pop('args'))
    task['args'] = args
    return task


def _restart_task(task: Dict, scheduler: Scheduler) -> None:
    parsed_task = _parse_task(task)
    func = handlers[parsed_task['name']]
    _start_task(
        scheduler,
        function=func,
        args=parsed_task['args'],
        time_args=parsed_task['time_args'],
    )


async def recreate_tasks(db: Engine, scheduler: Scheduler) -> None:
    tasks = await _get_tasks(db)
    if not tasks:
        return
    for task in tasks:
        _restart_task(task, scheduler)


async def _get_tasks(db: Engine) -> List[Dict]:
    async with db.acquire() as conn:
        return [dict(task) async for task in conn.execute(cron_task.select())]
