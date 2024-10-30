# Minimal RPC implementation over TCP, HTTP and MQTT
# Warning: using this module will disable python automatic gc

import gc
import sys
import json
import asyncio

import lib.log as _log
import lib.device_config as _dconf
import lib.mqtt as _mqtt
import lib.mediator as _mediator


def _test_rpc_handler(args: dict) -> tuple[bool, str]:
    return True, 'SERVER_ONLINE'


def _lwt_rpc_handler(args: dict) -> tuple[bool, str]:
    return True, 'DEVICE_ONLINE'


def _shell_rpc_handler(args: dict) -> tuple[bool, str]:
    device_password = args.get('device_password', None)
    script = args.get('script', None)
    if device_password != _dconf.get_conf('system.device_password'):
        return False, 'Invalid Device Password'
    if not script:
        return False, 'Missing `script` Key'
    try:
        return True, str(eval(script))
    except Exception as e:
        return False, f"Shell Error: {e}"


def _enable_usb_rpc_handler(args: dict) -> tuple[bool, str]:
    device_password = args.get('device_password', None)
    if device_password != _dconf.get_conf('system.device_password'):
        return False, 'Invalid Device Password'
    if sys.implementation.name == 'micropython':
        import os
        import machine  # type: ignore
        os.dupterm(machine.UART(0, 115200), 1)
    return True, 'OK'


_tcp_host = '0.0.0.0'
_tcp_port = 6540
_http_api_root = '/rpc'
_enable_http_tcp = False
_tcp_handlers_map: dict = None
_http_handlers_map: dict = None

mqtt_device_id = _dconf.get_conf('system.device_uuid')[-4:]
_lwt_mqtt_topic = 'telem/' + mqtt_device_id + '/lwt'
_log_mqtt_topic = 'telem/' + mqtt_device_id + '/log'
_state_mqtt_topic = 'state/' + mqtt_device_id
_enable_mqtt = False
_mqtt_handlers_map: dict = None


def _create_http_response(http_version: str, status_code: int, body: str = '') -> str:
    status_text_map = {
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found',
    }
    return '\r\n'.join([
        f"{http_version} {status_code} {status_text_map[status_code]}",
        'Content-Type: text/plain',
        'Content-Length: ' + str(len(body)),
        'Access-Control-Allow-Origin: *',
        '\r\n' + body,
    ])


def _url_unquote(inp: str):
    clean_plus = inp.replace('+', ' ')
    query_parts = clean_plus.split('%')
    decoded_query_value = [chr(int(x[:2], 16)) + x[2:] for x in query_parts[1:]]
    return query_parts[0] + ''.join(decoded_query_value)


def _parse_http_query(query: str) -> dict:
    out = {}
    if not query:
        return out
    query_pairs = query.split('&')
    for pair in query_pairs:
        qsp_k, qsp_v = [_url_unquote(x) for x in pair.split('=', 1)]
        out[qsp_k] = qsp_v
    return out


async def _core_handler_http(rpc_call_parts: list[str], sw: asyncio.StreamWriter):
    http_request, http_version = rpc_call_parts[1].split(' ', 1)
    http_version = http_version[:-1]
    if '?' in http_request:
        http_resource, http_query = http_request.split(' ', 1)[0].split('?', 1)
        parsed_query = _parse_http_query(http_query)
    else:
        http_resource = http_request.split(' ')[0].split('?')[0]
        parsed_query = {}

    if http_resource not in _http_handlers_map:
        sw.write(_create_http_response(http_version, 404).encode())
        return

    http_handler = _http_handlers_map[http_resource]
    http_handler_success, http_handler_output = http_handler(parsed_query)
    if http_handler_success:
        http_response = _create_http_response(http_version, 200, http_handler_output)
        sw.write(http_response.encode())
    else:
        http_response = _create_http_response(http_version, 400, http_handler_output)
        sw.write(http_response.encode())


async def _core_handler_tcp(rpc_call_parts: list[str], sw: asyncio.StreamWriter):
    func_name = rpc_call_parts[0]
    args = {}
    try:
        args = json.loads(rpc_call_parts[1])
    except:
        pass
    if func_name in _tcp_handlers_map:
        handler_output: str = _tcp_handlers_map[func_name](args)[1]
        sw.write(handler_output.encode())
    else:
        sw.write(f"Invalid RPC Call `{func_name}`".encode())


async def _http_tcp_core_handler(sr: asyncio.StreamReader, sw: asyncio.StreamWriter):
    _log.dlog('Received TCP Connection from ' + str(sw.get_extra_info('peername')))
    rpc_call = await sr.readline()
    rpc_call = rpc_call[:-1].decode()
    rpc_call_parts = rpc_call.split(' ', 1)
    func_name = rpc_call_parts[0]
    if func_name == 'GET':
        await _core_handler_http(rpc_call_parts, sw)
    else:
        await _core_handler_tcp(rpc_call_parts, sw)
    sw.close()
    await sw.wait_closed()
    gc.collect()


async def _http_tcp_server_task():
    _log.ilog(f"HTTP/TCP RPC Server Running on {_tcp_host}: {_tcp_port}")
    await asyncio.start_server(_http_tcp_core_handler, _tcp_host, _tcp_port)


def _core_handler_mqtt(topic: str, payload: str):
    _log.dlog(f'Received MQTT Msg topic={topic}, payload={payload}')
    if topic == 'telem/broadcast' and payload == 'DEVICES_SCAN':
        _mqtt.mqtt_publish(_lwt_mqtt_topic, 'ONLINE')
        gc.collect()
        return

    if topic.startswith('rpc/'):
        mqtt_rpc_handler_name = topic.split('/')[2]
        if mqtt_rpc_handler_name not in _mqtt_handlers_map:
            _log.elog('Invalid MQTT RPC Call: ' + topic)
            gc.collect()
            return
        args = {}
        try:
            args = json.loads(payload)
        except:
            pass
        handler_output: str = _mqtt_handlers_map[mqtt_rpc_handler_name](args)[1]
        _log.ilog('MQTT RPC Handler Response: ' + handler_output)
        device_pref = mqtt_rpc_handler_name.split('command_')[1]
        _mqtt.mqtt_publish(f'{_state_mqtt_topic}/{device_pref}', handler_output)
        gc.collect()
        return

    _log.elog('Invalid MQTT Topic: ' + topic)
    gc.collect()


def add_handler(func_name, func):
    if _enable_http_tcp:
        _tcp_handlers_map[func_name] = func
        _http_handlers_map[f'{_http_api_root}/{func_name}'] = func
    if _enable_mqtt:
        _mqtt_handlers_map[func_name] = func


def enable_mqtt_remote_logger():
    _log.enable_remote_logger()
    _mediator.subscribe('network_log', 'rpc.network_log', lambda log_msg: _mqtt.mqtt_publish(_log_mqtt_topic, log_msg))


def init_zeos_http_tcp_rpc():
    global _enable_http_tcp
    global _tcp_handlers_map
    global _http_handlers_map

    gc.disable()
    _enable_http_tcp = True
    _tcp_handlers_map = {
        'test': _test_rpc_handler,
        'lwt': _lwt_rpc_handler,
        'shell': _shell_rpc_handler,
        'enable_usb': _enable_usb_rpc_handler,
    }
    _http_handlers_map = {
        _http_api_root + '/test': _test_rpc_handler,
        _http_api_root + '/lwt': _lwt_rpc_handler,
    }
    gc.collect()
    return _http_tcp_server_task


def init_zeos_mqtt_rpc():
    global _enable_mqtt
    global _mqtt_handlers_map

    gc.disable()
    _enable_mqtt = True
    _mqtt_handlers_map = {}
    mqtt_client_task = _mqtt.mqtt_connect([
        'telem/broadcast',
        'rpc/' + mqtt_device_id + '/#',
    ], _core_handler_mqtt)
    gc.collect()
    return mqtt_client_task
