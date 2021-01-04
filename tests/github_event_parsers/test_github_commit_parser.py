from datetime import datetime

import pytest
from aiohttp import ClientSession

from src.services.github.base import USER_ACTIVITY, GithubEvent, GithubEventType
from src.services.github.commit_parser import CommitParser
from src.services.user_activity import UserActivity


@pytest.fixture()
def push_event(datetime_):
    return GithubEvent(
        created_at=datetime_,
        type=GithubEventType.Push,
        payload={
            'commits': [
                {
                    'url': 'https://api.github.com/repos/MakzaR/stepik_http_server/commits/58cfb9d8ec7da7e0364fcc5a1ccd3ef0f37508e6'
                }
            ]
        },
    )


@pytest.mark.asyncio
async def test_commit_time_shapes_correctly(push_event, mocker):
    patched_get_commit_func = mocker.patch(
        'src.services.github.commit_parser._get_github_commit_time'
    )
    created_at = datetime(1999, 12, 24, 12, 0)
    patched_get_commit_func.return_value = created_at
    res = await CommitParser(push_event, ClientSession()).parse()
    assert [UserActivity(f'{USER_ACTIVITY} CommitEvent', created_at, created_at)] == res
