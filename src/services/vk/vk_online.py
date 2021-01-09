from dataclasses import dataclass
from typing import List

from src.services.user_activity import UserActivity


@dataclass
class VkOnlineNode:
    is_online: bool
    last_online: str


def get_vk_online(online_nodes: List[VkOnlineNode]) -> List[UserActivity]:
    pass
