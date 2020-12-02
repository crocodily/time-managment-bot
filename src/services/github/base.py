from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel

from src.services.user_activity import UserActivity

USER_ACTIVITY = 'github'


class GithubEventType(Enum):
    Push = 'PushEvent'
    Issue = 'IssuesEvent'
    IssueComment = 'IssueCommentEvent'
    PullRequestReview = 'PullRequestReviewEvent'
    PullRequestReviewComment = 'PullRequestReviewCommentEvent'
    CommitComment = 'CommitCommentEvent'
    CreateBranch = 'CreateEvent'
    DeleteBranch = 'DeleteEvent'
    Fork = 'ForkEvent'
    Wiki = 'WikiEvent'
    Member = 'MemberEvent'
    Public = 'PublicEvent'
    PullRequest = 'PullRequestEvent'
    Release = 'ReleaseEvent'
    Sponsorship = 'SponsorshipEvent'
    Watch = 'WatchEvent'


class GithubEvent(BaseModel):
    type: GithubEventType
    created_at: datetime
    payload: Dict


class GithubEventParser(ABC):
    def __init__(self, event: GithubEvent):
        self._event = event

    @abstractmethod
    async def parse(self) -> List[UserActivity]:
        pass