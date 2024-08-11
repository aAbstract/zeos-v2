from _test_conf import *


def test_switch_state_power_0():
    _state = make_tcp_request('switch_state_power_0')
    assert _state == 'SWITCH_STATE_OFF'


def test_switch_command_power_0():
    _state = make_tcp_request('switch_command_power_0', {'command': 'ON'}, add_password=True)
    assert _state == 'SWITCH_STATE_ON'

    _state = make_tcp_request('switch_command_power_0', {'command': 'OFF'}, add_password=True)
    assert _state == 'SWITCH_STATE_OFF'

    _state = make_tcp_request('switch_command_power_0', {'command': 'TOGGLE'}, add_password=True)
    assert _state == 'SWITCH_STATE_ON'

    make_tcp_request('switch_command_power_0', {'command': 'OFF'}, add_password=True)
