import requests
from _test_conf import *


def test_server_online():
    http_res = requests.get(API_URL + '/test')
    assert http_res.json() == 'SERVER_ONLINE'


def test_shell_lock():
    http_res = requests.post(API_URL + '/shell')
    assert http_res.status_code == 401
    assert http_res.json() == 'UNAUTHORIZED'

    http_res = requests.post(API_URL + '/shell', headers={'x-device-password': 'fake_device_password'})
    assert http_res.status_code == 401
    assert http_res.json() == 'UNAUTHORIZED'


def test_shell_bad_request():
    http_res = requests.post(API_URL + '/shell', headers={'x-device-password': 'device_pass_123'})
    assert http_res.status_code == 400
    assert http_res.json() == 'Missing JSON Body'

    http_res = requests.post(API_URL + '/shell', headers={'x-device-password': 'device_pass_123'}, json={'k': 'v'})
    assert http_res.status_code == 400
    assert http_res.json() == 'Missing `script` Key'


def test_shell_success():
    http_res = requests.post(API_URL + '/shell', headers={'x-device-password': 'device_pass_123'}, json={'script': "_dconf.get_conf('device_uuid')"})
    assert http_res.status_code == 200
    assert http_res.json() == '00000000-0000-0000-0000-000000000000'


def test_device_lwt_protocol():
    http_res = requests.get(API_URL + f"/telem/{device_uuid}/DEVICE_LWT")
    assert http_res.status_code == 200
    assert http_res.json() == 'DEVICE_ONLINE'


def test_get_device_logs_lock():
    http_res = requests.get(API_URL + '/logs', headers={'x-device-password': 'fake_device_password'})
    assert http_res.status_code == 401
    assert http_res.json() == 'UNAUTHORIZED'


def test_get_device_logs_success():
    http_res = requests.get(API_URL + '/logs', headers={'x-device-password': 'device_pass_123'})
    assert http_res.status_code == 200
    _logs = http_res.json()
    assert isinstance(_logs, list)
    if len(_logs) > 0:
        assert isinstance(_logs[0], str)
