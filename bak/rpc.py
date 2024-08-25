import gc
import sys
import json
import asyncio

import lib.log as _log
import lib.device_config as _dconf
import lib.mqtt as _mqtt
import lib.mediator as _mediator


def _test(args: dict) -> tuple[bool, str]:
    return True, 'SERVER_ONLINE'


def _lwt(args: dict) -> tuple[bool, str]:
    return True, 'DEVICE_ONLINE'


def _shell(args: dict) -> tuple[bool, str]:
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


def _enable_usb(args: dict) -> tuple[bool, str]:
    device_password = args.get('device_password', None)
    if device_password != _dconf.get_conf('system.device_password'):
        return False, 'Invalid Device Password'
    if sys.implementation.name == 'micropython':
        import os
        import machine  # type: ignore
        os.dupterm(machine.UART(0, 115200), 1)
    return True, 'OK'


class RPCServer:
    '''
    Minimal RPC implementation over TCP, HTTP and MQTT
    Warning: using this module will disable python automatic gc
    '''
    _instance_id: int = 0
    _http_api_root = '/rpc'
    _lwt_mqtt_topic = None
    _log_mqtt_topic = None
    _state_mqtt_topic = None
    _mqtt_device_id = None

    host: str
    port: int
    instance_id: int

    enable_mqtt: bool
    mqtt_client_task = None

    tcp_handlers_map: dict
    http_handlers_map: dict
    mqtt_handlers_map: dict

    @staticmethod
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

    @staticmethod
    def _url_unquote(inp: str):
        clean_plus = inp.replace('+', ' ')
        query_parts = clean_plus.split('%')
        decoded_query_value = [chr(int(x[:2], 16)) + x[2:] for x in query_parts[1:]]
        return query_parts[0] + ''.join(decoded_query_value)

    @staticmethod
    def _parse_http_query(query: str) -> dict:
        out = {}
        if not query:
            return out
        query_pairs = query.split('&')
        for pair in query_pairs:
            qsp_k, qsp_v = [RPCServer._url_unquote(x) for x in pair.split('=', 1)]
            out[qsp_k] = qsp_v
        return out

    async def _core_handler_http(self, rpc_call_parts: list[str], sw: asyncio.StreamWriter):
        http_request, http_version = rpc_call_parts[1].split(' ', 1)
        http_version = http_version[:-1]
        if '?' in http_request:
            http_resource, http_query = http_request.split(' ', 1)[0].split('?', 1)
            parsed_query = RPCServer._parse_http_query(http_query)
        else:
            http_resource = http_request.split(' ')[0].split('?')[0]
            parsed_query = {}

        if http_resource not in self.http_handlers_map:
            sw.write(RPCServer._create_http_response(http_version, 404).encode())
            return

        http_handler = self.http_handlers_map[http_resource]
        http_handler_success, http_handler_output = http_handler(parsed_query)
        if http_handler_success:
            http_response = RPCServer._create_http_response(http_version, 200, http_handler_output)
            sw.write(http_response.encode())
        else:
            http_response = RPCServer._create_http_response(http_version, 400, http_handler_output)
            sw.write(http_response.encode())

    def _core_handler_mqtt(self, topic: str, payload: str):
        _log.dlog(f'Received MQTT Msg topic={topic}, payload={payload}')
        if topic == 'telem/broadcast' and payload == 'DEVICES_SCAN':
            _mqtt.mqtt_publish(RPCServer._lwt_mqtt_topic, 'ONLINE')
            gc.collect()
            return

        if topic.startswith('rpc/'):
            mqtt_rpc_handler_name = topic.split('/')[2]
            if mqtt_rpc_handler_name not in self.mqtt_handlers_map:
                _log.elog('Invalid MQTT RPC Call: ' + topic)
                gc.collect()
                return
            args = {}
            try:
                args = json.loads(payload)
            except:
                pass
            handler_output: str = self.mqtt_handlers_map[mqtt_rpc_handler_name](args)[1]
            _log.ilog('MQTT RPC Handler Response: ' + handler_output)
            device_pref = mqtt_rpc_handler_name.split('command_')[1]
            _mqtt.mqtt_publish(f'{RPCServer._state_mqtt_topic}/{device_pref}', handler_output)
            gc.collect()
            return

        _log.elog('Invalid MQTT Topic: ' + topic)
        gc.collect()

    async def _core_handler_tcp(self, rpc_call_parts: list[str], sw: asyncio.StreamWriter):
        func_name = rpc_call_parts[0]
        args = {}
        try:
            args = json.loads(rpc_call_parts[1])
        except:
            pass
        if func_name in self.tcp_handlers_map:
            handler_output: str = self.tcp_handlers_map[func_name](args)[1]
            sw.write(handler_output.encode())
        else:
            sw.write(f"Invalid RPC Call `{func_name}`".encode())

    async def _core_handler(self, sr: asyncio.StreamReader, sw: asyncio.StreamWriter):
        _log.dlog('Received TCP Connection from ' + str(sw.get_extra_info('peername')))
        rpc_call = await sr.readline()
        rpc_call = rpc_call[:-1].decode()
        rpc_call_parts = rpc_call.split(' ', 1)
        func_name = rpc_call_parts[0]
        if func_name == 'GET':
            await self._core_handler_http(rpc_call_parts, sw)
        else:
            await self._core_handler_tcp(rpc_call_parts, sw)
        sw.close()
        await sw.wait_closed()
        gc.collect()

    def __init__(self, _enable_mqtt=False) -> None:
        gc.disable()
        self.instance_id = RPCServer._instance_id
        RPCServer._instance_id += 1
        self.enable_mqtt = _enable_mqtt
        self.host = '0.0.0.0'
        self.port = int('654' + str(self.instance_id))
        self.tcp_handlers_map = {
            'test': _test,
            'lwt': _lwt,
            'shell': _shell,
            'enable_usb': _enable_usb,
        }
        self.http_handlers_map = {
            RPCServer._http_api_root + '/test': _test,
            RPCServer._http_api_root + '/lwt': _lwt,
        }

        # init mqtt client
        if not self.enable_mqtt:
            return
        RPCServer._mqtt_device_id = _dconf.get_conf('system.device_uuid')[-4:]
        RPCServer._lwt_mqtt_topic = 'telem/' + RPCServer._mqtt_device_id + '/lwt'
        RPCServer._log_mqtt_topic = 'telem/' + RPCServer._mqtt_device_id + '/log'
        RPCServer._state_mqtt_topic = 'state/' + RPCServer._mqtt_device_id
        self.mqtt_handlers_map = {}
        self.mqtt_client_task = _mqtt.mqtt_connect([
            'telem/broadcast',
            'rpc/' + RPCServer._mqtt_device_id + '/#',
        ], self._core_handler_mqtt)
        if not self.mqtt_client_task:
            return
        _log.enable_remote_logger()
        _mediator.subscribe('network_log', 'rpc.network_log', lambda log_msg: _mqtt.mqtt_publish(RPCServer._log_mqtt_topic, log_msg))
        gc.collect()

    async def server_task(self):
        _log.ilog(f"Registered RPCServer_{self.instance_id} Task")
        _log.ilog(f"RPC Server Running on {self.host}:{self.port}")
        await asyncio.start_server(self._core_handler, self.host, self.port)

    def add_handler(self, func_name, func):
        self.tcp_handlers_map[func_name] = func
        self.http_handlers_map[f'{RPCServer._http_api_root}/{func_name}'] = func
        if self.enable_mqtt:
            self.mqtt_handlers_map[func_name] = func
