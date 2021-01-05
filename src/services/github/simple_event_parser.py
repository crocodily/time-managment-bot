from typing import List

from src.services.github.base import USER_ACTIVITY, GithubEventParser
from src.services.user_activity import UserActivity


class SimpleEventParser(GithubEventParser):
    async def parse(self) -> List[UserActivity]:
        return [
            UserActivity(
                f'{USER_ACTIVITY} {self._event.type.value}',
                self._event.created_at,
                self._event.created_at,
            )
        ]
