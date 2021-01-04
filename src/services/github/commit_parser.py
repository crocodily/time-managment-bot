import asyncio
import logging
from datetime import datetime
from http import HTTPStatus
from typing import List

from aiohttp import ClientSession
from pydantic import BaseModel, ValidationError

from src.services.github.base import USER_ACTIVITY, GithubEvent, GithubEventParser
from src.services.user_activity import UserActivity


class Author(BaseModel):
    date: datetime


class Commit(BaseModel):
    author: Author


class CommitResponse(BaseModel):
    commit: Commit


class CommitPushEvent(BaseModel):
    url: str


class PayloadPushEvent(BaseModel):
    commits: List[CommitPushEvent]


async def _get_github_commit_time(commit_link: str, session: ClientSession) -> datetime:
    async with session.get(commit_link) as resp:
        if resp.status != HTTPStatus.OK:
            raise RuntimeError(f'Не найден коммит по ссылке {commit_link}')
        try:
            commit_response = CommitResponse(**await resp.json())
        except ValidationError as e:
            print(e)
    return commit_response.commit.author.date


class CommitParser(GithubEventParser):
    def __init__(self, event: GithubEvent, session: ClientSession):
        super().__init__(event)
        self.session = session

    async def parse(self) -> List[UserActivity]:
        commits = PayloadPushEvent(**self.event.payload).commits

        dates = await asyncio.gather(
            *[_get_github_commit_time(commit.url, self.session) for commit in commits],
            return_exceptions=True,
        )
        res = []
        for date in dates:
            if isinstance(date, BaseException):
                logging.error(date)
                continue
            res.append(UserActivity(f'{USER_ACTIVITY} CommitEvent', date, date))
        return res
