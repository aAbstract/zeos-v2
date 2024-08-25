import time
from _test_conf import *


NET_DELAY = 0.1


def _tcp_collect_relays_state() -> set[str]:
    state_set = set()
    for i in range(4):
        _state = make_tcp_request(f'state_power_{i}')
        state_set.add(_state)
        time.sleep(NET_DELAY)
    return state_set


def _assert_relays_state(_rs: set, target_state: str):
    assert len(_rs) == 1
    assert list(_rs)[0] == target_state


def _tcp_command_all_relays() -> set[str]:
    state_set = set()
    for i in range(4):
        _state = make_tcp_request(f'command_power_{i}')
        state_set.add(_state)
        time.sleep(NET_DELAY)
    return state_set


def test_switch_module_tcp():
    _assert_relays_state(_tcp_collect_relays_state(), 'RELAY_STATE_OFF')
    _assert_relays_state(_tcp_command_all_relays(), 'RELAY_STATE_ON')
    _assert_relays_state(_tcp_collect_relays_state(), 'RELAY_STATE_ON')
    _assert_relays_state(_tcp_command_all_relays(), 'RELAY_STATE_OFF')
    _assert_relays_state(_tcp_collect_relays_state(), 'RELAY_STATE_OFF')
