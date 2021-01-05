import logging

from aiohttp import ClientSession

from src.services.github.github import get_github_activity


async def test(user_name: str, session: ClientSession, access_token: str, **_) -> None:
    res = await get_github_activity(user_name, access_token, session)
    logging.info(res)


handlers = {'test': test}
