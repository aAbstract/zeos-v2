import time
from _test_conf import *


def _collect_relays_state() -> set[str]:
    return {
        make_tcp_request('switch_state_power_0'),
        make_tcp_request('switch_state_power_1'),
        make_tcp_request('switch_state_power_2'),
        make_tcp_request('switch_state_power_3'),
    }


def _assert_relays_state(_rs: set, target_state: str):
    assert len(_rs) == 1
    assert list(_rs)[0] == target_state


def _command_all_relays() -> set[str]:
    return {
        make_tcp_request('switch_command_power_0'),
        make_tcp_request('switch_command_power_1'),
        make_tcp_request('switch_command_power_2'),
        make_tcp_request('switch_command_power_3'),
    }


def test_switch():
    net_delay = 0.2
    _assert_relays_state(_collect_relays_state(), 'RELAY_STATE_OFF')
    time.sleep(net_delay)
    _assert_relays_state(_command_all_relays(), 'RELAY_STATE_ON')
    time.sleep(net_delay)
    _assert_relays_state(_collect_relays_state(), 'RELAY_STATE_ON')
    time.sleep(net_delay)
    _assert_relays_state(_command_all_relays(), 'RELAY_STATE_OFF')
    time.sleep(net_delay)
    _assert_relays_state(_collect_relays_state(), 'RELAY_STATE_OFF')
    time.sleep(net_delay)
