# autopep8: off
import os
import sys
import asyncio

if sys.implementation.name == 'micropython':
    import machine # type: ignore
sys.path.append(os.getcwd())

import lib.device_config as _dconf
import lib.log as _log
import lib.wifi as _wifi
import lib.rpc as _rpc
# autopep8: on


MODULE_NAME = 'SWITCH'
RELAY_STATE_ON = 0
RELAY_STATE_OFF = 1

touch_led_states = {
    b'\x11': 0xA0,
    b'\x21': 0xB0,
    b'\x31': 0xC0,
    b'\x41': 0xD0,
}

_wifi.wifi_connect()
rpc_server = _rpc.RPCServer(_enable_mqtt=True)
if sys.implementation.name == 'micropython':
    power_0 = machine.Pin(5, machine.Pin.OUT)
    power_1 = machine.Pin(4, machine.Pin.OUT)
    power_2 = machine.Pin(13, machine.Pin.OUT)
    power_3 = machine.Pin(14, machine.Pin.OUT)
    touch_panel_uart: machine.UART = None
    relay_map = {
        b'\x11': power_0,
        b'\x21': power_1,
        b'\x31': power_2,
        b'\x41': power_3,
    }


def mod_setup():
    rpc_server.add_handler('switch_command_power_0', lambda _: handle_touch_input_code(b'\x11'))
    rpc_server.add_handler('switch_command_power_1', lambda _: handle_touch_input_code(b'\x21'))
    rpc_server.add_handler('switch_command_power_2', lambda _: handle_touch_input_code(b'\x31'))
    rpc_server.add_handler('switch_command_power_3', lambda _: handle_touch_input_code(b'\x41'))
    rpc_server.add_handler('switch_state_power_0', lambda _: (True, 'RELAY_STATE_ON') if touch_led_states[b'\x11'] % 2 == 1 else (True, 'RELAY_STATE_OFF'))
    rpc_server.add_handler('switch_state_power_1', lambda _: (True, 'RELAY_STATE_ON') if touch_led_states[b'\x21'] % 2 == 1 else (True, 'RELAY_STATE_OFF'))
    rpc_server.add_handler('switch_state_power_2', lambda _: (True, 'RELAY_STATE_ON') if touch_led_states[b'\x31'] % 2 == 1 else (True, 'RELAY_STATE_OFF'))
    rpc_server.add_handler('switch_state_power_3', lambda _: (True, 'RELAY_STATE_ON') if touch_led_states[b'\x41'] % 2 == 1 else (True, 'RELAY_STATE_OFF'))


def handle_touch_input_code(_tic: bytes) -> tuple[bool, str]:
    if _tic not in touch_led_states:
        return False, 'Invalid Touch Input Code'

    # compute new led state
    target_led_state = touch_led_states[_tic]
    new_led_state = target_led_state - 1 if target_led_state % 2 == 1 else target_led_state + 1
    touch_led_states[_tic] = new_led_state

    # control target relay
    target_relay = relay_map[_tic]
    new_relay_state = RELAY_STATE_ON if new_led_state % 2 == 1 else RELAY_STATE_OFF
    target_relay.value(new_relay_state)

    # control target touch led
    # touch_panel_uart.write(bytes([new_led_state]))

    return True, 'RELAY_STATE_ON' if new_relay_state == RELAY_STATE_ON else 'RELAY_STATE_OFF'


async def mod_loop():
    _log.ilog('Registered Module Task: ' + MODULE_NAME, 'modules.switch.mod_loop')
    while True:
        if sys.implementation.name == 'micropython' and touch_panel_uart:
            if touch_panel_uart.any() > 0:
                handle_touch_input_code(touch_panel_uart.read(1))
            await asyncio.sleep(0.01)  # 100 Hz
            continue
        await asyncio.sleep(1)


async def detach_uart_0_task():
    global touch_panel_uart
    _log.ilog('Detaching REPL from UART_0')
    machine.Pin(2, machine.Pin.OUT).value(0)
    touch_panel_uart = os.dupterm(None, 1)
    touch_panel_uart.write(b'\xA1')


async def mqtt_client_loop():
    while True:
        rpc_server.mqtt_client_task()
        await asyncio.sleep(0.1)


async def boot_zeos():
    mod_setup()
    rpc_server_task = asyncio.create_task(rpc_server.server_task())
    mqtt_client_task = asyncio.create_task(mqtt_client_loop())
    module_task = asyncio.create_task(mod_loop())
    # _detach_uart_0_task = asyncio.create_task(detach_uart_0_task())
    await asyncio.gather(
        rpc_server_task,
        mqtt_client_task,
        module_task,
        # _detach_uart_0_task,
    )


def boot_repl():
    global touch_panel_uart
    import webrepl  # type: ignore
    webrepl.start(password=_dconf.get_conf('system.device_password'))
    touch_panel_uart = os.dupterm(None, 1)


if __name__ == '__main__':
    boot_mode = _dconf.get_conf('system.boot_mode')
    _log.ilog('Boot Mode ' + boot_mode, 'modules.switch.main')
    if boot_mode == 'ZEOS':
        asyncio.run(boot_zeos())
    elif boot_mode == 'REPL' and sys.implementation.name == 'micropython':
        boot_repl()
