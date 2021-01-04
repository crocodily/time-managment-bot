from typing import List

from aiohttp import ClientSession
from pydantic import parse_obj_as

from src.services.github.base import GithubEvent, GithubEventParser, GithubEventType
from src.services.github.factory import get_event_parser
from src.services.user_activity import UserActivity


async def _get_github_events(
    user_name: str, clientSession: ClientSession
) -> List[GithubEvent]:
    async with clientSession.get(
        f'https://api.github.com/users/{user_name}/events'
    ) as response:
        data = await response.json()
        return parse_obj_as(List[GithubEvent], data)


def _get_event_parsers(
    events: List[GithubEvent], session: ClientSession
) -> List[GithubEventParser]:
    event_parsers: List[GithubEventParser] = []
    for event in events:
        if event.type not in [
            GithubEventType.Push,
            GithubEventType.PullRequestReview,
            GithubEventType.PullRequestReviewComment,
            GithubEventType.IssueComment,
            GithubEventType.Issue,
        ]:
            continue
        event_parsers.append(get_event_parser(event, session))
    return event_parsers


async def get_github_activity(
    user_name: str, session: ClientSession
) -> List[UserActivity]:
    github_events = await _get_github_events(user_name, session)
    event_parsers = _get_event_parsers(github_events, session)
    result = []
    for event_parser in event_parsers:
        result += await event_parser.parse()
    return result
