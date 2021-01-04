import asyncio

from aiohttp import ClientSession

from src.services.github.github import get_github_activity

# пример получения информации о пользователе
# async def main():
#     async with ClientSession() as session:
#         res = await get_github_activity('nesb1', session)
#         for r in res:
#             print(r)
#
#
# asyncio.run(main())
