from datetime import datetime

from aiohttp import ClientSession

from src.services.github.base import GithubEvent, GithubEventParser, GithubEventType
from src.services.github.commit_parser import CommitParser
from src.services.github.simple_event_parser import SimpleEventParser


def get_event_parser(
        event: GithubEvent, session: ClientSession, access_token: str, from_time_utc: datetime
) -> GithubEventParser:
    if event.type == GithubEventType.Push:
        return CommitParser(event, from_time_utc, session, access_token)
    return SimpleEventParser(event, from_time_utc)
