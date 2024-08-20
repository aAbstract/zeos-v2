import urllib.parse as urlp
from lib.rpc import RPCServer


def test_url_decoder():
    test_cases_base = [
        {},
        {'device_password': 'device_pass_123', 'script': '_dconf.get_conf("system.device_uuid")'},
        {'str_key_1': 'str_value_1', 'str_key_2': 'str_value_2'},
        {'num_key_1': '11', 'num_key_2': '22'},
        {'mixed_str_key': 'mixed_str_value', 'mixed_num_key': '55', 'mixed_bool_1': '1', 'mixed_bool_2': '0'},
    ]

    # generate test cases
    test_cases = []
    for tc_base in test_cases_base:
        test_cases.append((urlp.urlencode(tc_base), tc_base))

    # run tests
    for query, target_output in test_cases:
        _output = RPCServer._parse_http_query(query)
        assert _output == target_output
