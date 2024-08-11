import requests
from _test_conf import *


def _get_switch_device_state() -> str:
    http_res = requests.get(API_URL + f"/state/{device_uuid}/power_0")
    assert http_res.status_code == 200
    return http_res.json()


def test_handle_switch_state_power_0():
    _state = _get_switch_device_state()
    assert _state == 'SWITCH_STATE_OFF'
