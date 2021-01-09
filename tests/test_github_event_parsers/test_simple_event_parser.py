import pytest

from src.services.github.base import USER_ACTIVITY, GithubEvent, GithubEventType
from src.services.github.simple_event_parser import SimpleEventParser
from src.services.user_activity import UserActivity


@pytest.fixture()
def event(datetime_):
    return GithubEvent(type=GithubEventType.Issue, created_at=datetime_, payload={})


@pytest.mark.asyncio
async def test_event_parser(event, datetime_):
    res = await SimpleEventParser(event).parse()
    expected = UserActivity(
        f'{USER_ACTIVITY} {GithubEventType.Issue.value}', datetime_, datetime_
    )
    assert res == [expected]
