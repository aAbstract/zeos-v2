def _get_logs(args: dict) -> tuple[bool, str]:
    device_password = args.get('device_password', None)
    if device_password != _dconf.get_conf('system.device_password'):
        return False, 'Invalid Device Password'
    return True, '\n'.join(_log.get_logs_tail())


def _test_get_device_logs_lock():
    tcp_res = make_tcp_request('get_logs', {'device_password': 'fake_device_password'})
    assert tcp_res == 'Invalid Device Password'


def _test_get_device_logs_success():
    tcp_res = make_tcp_request('get_logs', {'device_password': 'device_pass_123'})
    assert isinstance(tcp_res, str)
