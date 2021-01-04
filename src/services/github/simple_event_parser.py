from typing import List

from src.services.github.base import USER_ACTIVITY, GithubEventParser
from src.services.user_activity import UserActivity


class SimpleEventParser(GithubEventParser):
    async def parse(self) -> List[UserActivity]:
        return [
            UserActivity(
                f'{USER_ACTIVITY} {self.event.type.value}',
                self.event.created_at,
                self.event.created_at,
            )
        ]
