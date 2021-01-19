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
        format = '%Y-%m-%dT%H:%MZ'
        return {
            'serviceName': self.service_name,
            'description': self.description,
            'fromTime': self.from_time.strftime(format),
            'toTime': self.to_time.strftime(format),
        }
