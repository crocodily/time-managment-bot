from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass
class UserActivity:
    service_name: str
    description: str
    from_time: datetime
    to_time: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            'serviceName': self.service_name,
            'activityName': self.description,
            'fromTime': str(self.from_time),
            'toTime': str(self.to_time),
        }
