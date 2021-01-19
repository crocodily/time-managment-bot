from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from src.services.user_activity import UserActivity


@dataclass
class VkOnlineNode:
    is_online: bool
    last_online: datetime
    created_at: datetime


@dataclass
class CurrentOnline:
    start: datetime
    possible_end: datetime


def _remove_seconds_and_microseconds(time: datetime) -> datetime:
    return time.replace(second=0, microsecond=0)


def _make_current(node: VkOnlineNode, delta: timedelta) -> Optional[CurrentOnline]:
    if not node.is_online:
        return None
    return CurrentOnline(
        start=node.created_at,
        possible_end=_get_possible_end(node, delta),
    )


def _get_possible_end(node: VkOnlineNode, delta: timedelta) -> datetime:
    return node.created_at + delta / 2


def _merge(
    current: CurrentOnline, node: VkOnlineNode, delta: timedelta
) -> Tuple[Optional[CurrentOnline], Optional[UserActivity]]:
    if not node.is_online:
        return None, UserActivity('VK', 'online',current.start, node.last_online)
    return (
        CurrentOnline(
            start=current.start,
            possible_end=_get_possible_end(node, delta),
        ),
        None,
    )


def get_single_node_activity(
    node: VkOnlineNode, delta: timedelta
) -> Optional[UserActivity]:
    if not node.is_online:
        return None
    half_delta = delta / 2
    created_at = node.created_at
    return UserActivity(
        'VK', description='online',from_time=created_at - half_delta, to_time=created_at + half_delta
    )


def get_vk_online(
    online_nodes: List[VkOnlineNode], nodes_time_delta: timedelta
) -> List[UserActivity]:
    user_activities: List[UserActivity] = []
    if len(online_nodes) < 1:
        return user_activities
    if len(online_nodes) == 1:
        activity = get_single_node_activity(online_nodes[0], nodes_time_delta)
        if activity:
            user_activities.append(activity)
        return user_activities

    current: Optional[CurrentOnline] = None
    for node in online_nodes:
        current = current or _make_current(node, nodes_time_delta)
        if not current:
            continue
        current, user_activity = _merge(current, node, nodes_time_delta)
        if user_activity:
            user_activities.append(user_activity)
    if current:
        user_activities.append(
            UserActivity('VK', 'online', from_time=current.start, to_time=current.possible_end)
        )
    return user_activities
