from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserActivity:
    name: str
    from_time: datetime
    to_time: datetime
