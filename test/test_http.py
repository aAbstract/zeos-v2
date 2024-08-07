import requests

API_URL = 'http://127.0.0.1:8080/api'


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


def test_shell_success():
    http_res = requests.post(API_URL + '/shell', headers={'x-device-password': 'device_pass_123'}, json={'script': "_dconf.get_conf('device_uuid')"})
    assert http_res.status_code == 200
    assert http_res.json() == '00000000-0000-0000-0000-000000000000'
