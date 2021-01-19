from datetime import datetime, timedelta

import pytest

from src.services.user_activity import UserActivity
from src.services.vk.vk_online import VkOnlineNode, get_vk_online


@pytest.fixture()
def delta():
    return timedelta(minutes=10)


def test_one_active_node_online(datetime_, delta):
    nodes = [VkOnlineNode(is_online=True, last_online=datetime_, created_at=datetime_)]
    actual = get_vk_online(online_nodes=nodes, nodes_time_delta=delta)
    half_delta = delta / 2
    expected = [
        UserActivity(
            service_name='VK', description='online', from_time=datetime_ - half_delta, to_time=datetime_ + half_delta
        )
    ]
    assert actual == expected


def test_one_no_active_node(datetime_, delta):
    nodes = [
        VkOnlineNode(
            is_online=False,
            last_online=datetime_ - timedelta(hours=1),
            created_at=datetime.now(),
        )
    ]
    actual = get_vk_online(online_nodes=nodes, nodes_time_delta=delta)
    assert actual == []


def test_active_and_then_no_active_node(datetime_, delta):
    last_online = datetime_ - timedelta(minutes=2)
    nodes = [
        VkOnlineNode(
            is_online=True, last_online=datetime_ - delta, created_at=datetime_ - delta
        ),
        VkOnlineNode(is_online=False, last_online=last_online, created_at=datetime_),
    ]
    actual = get_vk_online(online_nodes=nodes, nodes_time_delta=delta)
    expected = [
        UserActivity(service_name='VK', description='online', from_time=datetime_ - delta, to_time=last_online)
    ]
    assert actual == expected


def test_two_close_active_nodes(datetime_, delta):
    nodes = [
        VkOnlineNode(
            is_online=True, last_online=datetime_ - delta, created_at=datetime_ - delta
        ),
        VkOnlineNode(is_online=True, last_online=datetime_, created_at=datetime_),
    ]
    actual = get_vk_online(online_nodes=nodes, nodes_time_delta=delta)
    expected = [
        UserActivity(
            service_name='VK', description='online', from_time=datetime_ - delta, to_time=datetime_ + 0.5 * delta
        )
    ]
    assert actual == expected


def test_two_close_offline_nodes(datetime_, delta):
    last_online = datetime_ - timedelta(hours=2)
    nodes = [
        VkOnlineNode(
            is_online=False, last_online=last_online, created_at=datetime_ - delta
        ),
        VkOnlineNode(is_online=False, last_online=last_online, created_at=datetime_),
    ]
    actual = get_vk_online(online_nodes=nodes, nodes_time_delta=delta)
    assert actual == []


def test_offline_and_then_online_node(datetime_, delta):
    nodes = [
        VkOnlineNode(
            is_online=False,
            last_online=datetime_ - timedelta(hours=2),
            created_at=datetime_ - delta,
        ),
        VkOnlineNode(is_online=True, last_online=datetime_, created_at=datetime_),
    ]
    actual = get_vk_online(online_nodes=nodes, nodes_time_delta=delta)
    expected = [
        UserActivity(service_name='VK', description='online', from_time=datetime_, to_time=datetime_ + 0.5 * delta)
    ]
    assert actual == expected


def test_online_offline_online_nodes(datetime_, delta):
    last_online = datetime_ - delta - timedelta(minutes=2)
    nodes = [
        VkOnlineNode(
            is_online=True,
            last_online=datetime_ - 2 * delta,
            created_at=datetime_ - 2 * delta,
        ),
        VkOnlineNode(
            is_online=False, last_online=last_online, created_at=datetime_ - delta
        ),
        VkOnlineNode(is_online=True, last_online=datetime_, created_at=datetime_),
    ]
    actual = get_vk_online(online_nodes=nodes, nodes_time_delta=delta)
    expected = [
        UserActivity(service_name='VK', description='online', from_time=datetime_ - 2 * delta, to_time=last_online),
        UserActivity(service_name='VK', description='online', from_time=datetime_, to_time=datetime_ + 0.5 * delta),
    ]
    assert actual == expected


def test_offline_online_offline_nodes(datetime_, delta):
    last_online = datetime_ - timedelta(minutes=2)
    nodes = [
        VkOnlineNode(
            is_online=False,
            last_online=datetime_ - timedelta(hours=2),
            created_at=datetime_ - 2 * delta,
        ),
        VkOnlineNode(
            is_online=True, last_online=datetime_ - delta, created_at=datetime_ - delta
        ),
        VkOnlineNode(is_online=False, last_online=last_online, created_at=datetime_),
    ]
    actual = get_vk_online(online_nodes=nodes, nodes_time_delta=delta)
    expected = [
        UserActivity(service_name='VK', description='online', from_time=datetime_ - delta, to_time=last_online),
    ]
    assert actual == expected
