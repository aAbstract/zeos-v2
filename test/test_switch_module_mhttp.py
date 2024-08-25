import time
import requests
from _test_conf import *


NET_DELAY = 0.1


def _http_collect_relays_state() -> set[str]:
    state_set = set()
    for i in range(4):
        _http_res = requests.get(f"{API_URL}/state_power_{i}")
        assert _http_res.status_code == 200
        state_set.add(_http_res.text)
        time.sleep(NET_DELAY)
    return state_set


def _assert_relays_state(_rs: set, target_state: str):
    assert len(_rs) == 1
    assert list(_rs)[0] == target_state


def _http_command_all_relays() -> set[str]:
    state_set = set()
    for i in range(4):
        _http_res = requests.get(f"{API_URL}/command_power_{i}")
        assert _http_res.status_code == 200
        state_set.add(_http_res.text)
        time.sleep(NET_DELAY)
    return state_set


def test_switch_module_mhttp():
    _assert_relays_state(_http_collect_relays_state(), 'RELAY_STATE_OFF')
    _assert_relays_state(_http_command_all_relays(), 'RELAY_STATE_ON')
    _assert_relays_state(_http_collect_relays_state(), 'RELAY_STATE_ON')
    _assert_relays_state(_http_command_all_relays(), 'RELAY_STATE_OFF')
    _assert_relays_state(_http_collect_relays_state(), 'RELAY_STATE_OFF')
