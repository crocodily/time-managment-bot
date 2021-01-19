import asyncio
import logging
from datetime import datetime
from http import HTTPStatus
from typing import List

from aiohttp import ClientSession
from pydantic import BaseModel

from src.services.github.base import USER_ACTIVITY, GithubEvent, GithubEventParser
from src.services.time import matches_the_time
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


async def _get_github_commit_time(
    commit_link: str, session: ClientSession, access_token: str
) -> datetime:
    async with session.get(
            commit_link, headers={'Authorization': f'token {access_token}'}
    ) as resp:
        if resp.status != HTTPStatus.OK:
            raise RuntimeError(f'Не найден коммит по ссылке {commit_link}')
        commit_response = CommitResponse(**await resp.json())
    return commit_response.commit.author.date


class CommitParser(GithubEventParser):
    def __init__(self, event: GithubEvent, from_time_utc: datetime, session: ClientSession, access_token: str):
        super().__init__(event, from_time_utc)
        self._client_session = session
        self._access_token = access_token

    async def parse(self) -> List[UserActivity]:
        commits = PayloadPushEvent(**self._event.payload).commits

        dates = await asyncio.gather(
            *[
                _get_github_commit_time(
                    commit.url, self._client_session, self._access_token
                )
                for commit in commits
            ],
            return_exceptions=True,
        )
        logging.debug(f'times: {dates}')
        res = []
        for commit_time in dates:
            if isinstance(commit_time, BaseException):
                logging.error(commit_time)
                continue
            if not matches_the_time(self._from_time_utc, commit_time):
                continue
            res.append(UserActivity(USER_ACTIVITY, 'commit', commit_time, commit_time))
        return res
