# autopep8: off
import os
import sys
import asyncio

if sys.implementation.name == 'micropython':
    import machine # type: ignore
sys.path.append(os.getcwd())

import lib.tcp as _tcp
import lib.log as _log
import lib.device_config as _dconf
import lib.wifi as _wifi
# autopep8: on


MODULE_NAME = 'SWITCH'
SWITCH_STATE_ON = 0
SWITCH_STATE_OFF = 1

_wifi.wifi_connect()
tcp_server = _tcp.TCPServer()
switch_state = SWITCH_STATE_OFF
if sys.implementation.name == 'micropython':
    power_0 = machine.Pin(2, machine.Pin.OUT)
    power_0.value(switch_state)


def switch_command_power_0(args: dict, sw: asyncio.StreamWriter) -> str | None:
    global switch_state
    device_password = args.get('device_password', None)
    if device_password != _dconf.get_conf('device_password'):
        sw.write('Invalid Device Password'.encode())
        return
    command = args.get('command', None)
    if not command:
        sw.write('Missing `command` Key')
        return
    command_map = {
        'ON': SWITCH_STATE_ON,
        'OFF': SWITCH_STATE_OFF,
        'TOGGLE': SWITCH_STATE_ON if switch_state == SWITCH_STATE_OFF else SWITCH_STATE_OFF
    }
    switch_state = command_map[command]
    if sys.implementation.name == 'micropython':
        power_0.value(switch_state)
    ret_str = 'SWITCH_STATE_ON' if switch_state == SWITCH_STATE_ON else 'SWITCH_STATE_OFF'
    return ret_str


def switch_state_power_0(args: dict, sw: asyncio.StreamWriter) -> str | None:
    ret_str = 'SWITCH_STATE_ON' if switch_state == SWITCH_STATE_ON else 'SWITCH_STATE_OFF'
    return ret_str


def mod_setup():
    tcp_server.add_rpc_handler('switch_command_power_0', switch_command_power_0)
    tcp_server.add_rpc_handler('switch_state_power_0', switch_state_power_0)


async def mod_loop():
    _log.ilog('Registered Module Task: ' + MODULE_NAME, 'modules.switch.mod_loop')
    while True:
        # module loop routine
        # print('MODULE LOOP')
        await asyncio.sleep(1)  # delay 5s


async def main():
    mod_setup()
    tcp_server_task = asyncio.create_task(tcp_server.server_task())
    module_task = asyncio.create_task(mod_loop())
    await asyncio.gather(
        tcp_server_task,
        module_task,
    )

if __name__ == '__main__':
    asyncio.run(main())
