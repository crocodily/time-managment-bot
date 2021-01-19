from datetime import timedelta

import pytest

from src.services.github.base import USER_ACTIVITY, GithubEvent, GithubEventType
from src.services.github.simple_event_parser import SimpleEventParser
from src.services.user_activity import UserActivity


@pytest.fixture()
def event(datetime_):
    return GithubEvent(type=GithubEventType.Issue, created_at=datetime_, payload={})


@pytest.mark.asyncio
async def test_event_parser(event, datetime_):
    res = await SimpleEventParser(event, datetime_).parse()
    expected = UserActivity(
        USER_ACTIVITY, GithubEventType.Issue.value, datetime_, datetime_
    )
    assert res == [expected]


@pytest.mark.asyncio
async def test_event_parser_drop_events_outside_work_day(event, datetime_):
    res = await SimpleEventParser(event, datetime_ + timedelta(minutes=5)).parse()
    assert res == []