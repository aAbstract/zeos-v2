import requests
from _test_conf import *


def test_server_online():
    http_res = requests.get(API_URL + '/test')
    assert http_res.status_code == 200
    assert http_res.text == 'SERVER_ONLINE'


def test_device_lwt_protocol():
    http_res = requests.get(API_URL + '/lwt')
    assert http_res.text == 'DEVICE_ONLINE'
