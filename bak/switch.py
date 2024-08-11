# autopep8: off
import os
import sys
import asyncio

if sys.implementation.name == 'micropython':
    import machine # type: ignore
sys.path.append(os.getcwd())

import lib.http as _http
import lib.log as _log
import lib.device_config as _dconf
import lib.wifi as _wifi
# autopep8: on


MODULE_NAME = 'SWITCH'
SWITCH_STATE_ON = 0
SWITCH_STATE_OFF = 1

_wifi.wifi_connect()
http_service = _http.HTTPService()
switch_state = SWITCH_STATE_OFF
if sys.implementation.name == 'micropython':
    power_0 = machine.Pin(2, machine.Pin.OUT)
    power_0.value(switch_state)


@http_service.mdt_server.route(_dconf.get_conf('http.api_root') + '/command/' + _dconf.get_conf('device_uuid') + '/power_0', methods=['POST'])
def handle_switch_command_power_0(request: _http.Request):
    req_headers: dict = request.headers
    device_password = req_headers.get('x-device-password', None)
    if device_password != _dconf.get_conf('device_password'):
        return _http.HTTPService.wrap_json_string('UNAUTHORIZED'), 401

    json_body = request.g.json_body
    if not json_body:
        return _http.HTTPService.wrap_json_string('Missing JSON Body'), 400

    if 'command' not in json_body:
        return _http.HTTPService.wrap_json_string('Missing `command` Key'), 400

    command = json_body['command']
    command_map = {
        'ON': SWITCH_STATE_ON,
        'OFF': SWITCH_STATE_OFF,
        'TOGGLE': SWITCH_STATE_ON if switch_state == SWITCH_STATE_OFF else SWITCH_STATE_OFF
    }
    switch_state = command_map[command]
    if sys.implementation.name == 'micropython':
        power_0.value(switch_state)
    ret_str = 'SWITCH_STATE_ON' if switch_state == SWITCH_STATE_ON else 'SWITCH_STATE_OFF'
    return _http.HTTPService.wrap_json_string(ret_str)


@http_service.mdt_server.route(_dconf.get_conf('http.api_root') + '/state/' + _dconf.get_conf('device_uuid') + '/power_0', methods=['GET'])
def handle_switch_state_power_0(request: _http.Request):
    ret_str = 'SWITCH_STATE_ON' if switch_state == SWITCH_STATE_ON else 'SWITCH_STATE_OFF'
    return _http.HTTPService.wrap_json_string(ret_str)


async def mod_loop():
    _log.ilog('Registered Module Task: ' + MODULE_NAME, 'modules.switch.mod_loop')
    while True:
        # module loop routine
        await asyncio.sleep(5)  # delay 5s


async def main():
    module_task = asyncio.create_task(mod_loop())
    http_server_task = asyncio.create_task(http_service.server_task())
    await asyncio.gather(
        http_server_task,
        module_task,
    )

if __name__ == '__main__':
    asyncio.run(main())
