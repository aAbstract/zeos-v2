import re
from _test_conf import *


def test_server_online():
    tcp_res = make_tcp_request('test')
    assert tcp_res == 'SERVER_ONLINE'


def test_shell_lock():
    tcp_res = make_tcp_request('shell')
    assert tcp_res == 'Invalid Device Password'
    tcp_res = make_tcp_request('shell', {'device_password': 'fake_device_password'})
    assert tcp_res == 'Invalid Device Password'


def test_shell_bad_request():
    tcp_res = make_tcp_request('shell', add_password=True)
    assert tcp_res == 'Missing `script` Key'


def test_shell_success():
    tcp_res = make_tcp_request('shell', {'script': '_dconf.get_conf("system.device_uuid")'}, add_password=True)
    assert re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', tcp_res)


def test_device_lwt_protocol():
    tcp_res = make_tcp_request('lwt')
    assert tcp_res == 'DEVICE_ONLINE'


def test_device_conf():
    device_uuid = make_tcp_request('shell', {'script': '_dconf.get_conf("system.device_uuid")'}, add_password=True)
    assert re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', device_uuid)

    make_tcp_request('shell', {'script': '_dconf.set_conf("system.device_uuid", "x")'}, add_password=True)
    tcp_res = make_tcp_request('shell', {'script': '_dconf.get_conf("system.device_uuid")'}, add_password=True)
    assert tcp_res == 'x'

    make_tcp_request('shell', {'script': f'_dconf.set_conf("system.device_uuid", "{device_uuid}")'}, add_password=True)
    tcp_res = make_tcp_request('shell', {'script': '_dconf.get_conf("system.device_uuid")'}, add_password=True)
    assert tcp_res == device_uuid
