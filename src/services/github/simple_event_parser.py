from typing import List

from src.services.github.base import USER_ACTIVITY, GithubEventParser
from src.services.time import matches_the_time
from src.services.user_activity import UserActivity


class SimpleEventParser(GithubEventParser):
    async def parse(self) -> List[UserActivity]:
        if not matches_the_time(self._from_time_utc, self._event.created_at):
            return []
        return [
            UserActivity(
                USER_ACTIVITY, self._event.type.value,
                self._event.created_at,
                self._event.created_at,
            )
        ]
