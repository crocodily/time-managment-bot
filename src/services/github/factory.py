from aiohttp import ClientSession

from src.services.github.base import GithubEvent, GithubEventParser, GithubEventType
from src.services.github.commit_parser import CommitParser
from src.services.github.simple_event_parser import SimpleEventParser


def get_event_parser(event: GithubEvent, session: ClientSession) -> GithubEventParser:
    if event.type == GithubEventType.Push:
        return CommitParser(event, session)
    return SimpleEventParser(event)
