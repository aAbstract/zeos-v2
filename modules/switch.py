# autopep8: off
import os
import gc
import sys
import asyncio

if sys.implementation.name == 'micropython':
    import machine # type: ignore
sys.path.append(os.getcwd())

import lib.device_config as _dconf
import lib.log as _log
import lib.wifi as _wifi
import lib.mqtt as _mqtt
import lib.rpc as _rpc
# autopep8: on

_wifi.wifi_connect()

MODULE_NAME = 'SWITCH'
RELAY_STATE_ON = 0
RELAY_STATE_OFF = 1

power_0 = None
power_1 = None
power_2 = None
power_3 = None
touch_panel_uart = None
if sys.implementation.name == 'micropython':
    power_0 = machine.Pin(5, machine.Pin.OUT)
    power_1 = machine.Pin(4, machine.Pin.OUT)
    power_2 = machine.Pin(13, machine.Pin.OUT)
    power_3 = machine.Pin(14, machine.Pin.OUT)
    power_0.value(RELAY_STATE_OFF)
    power_1.value(RELAY_STATE_OFF)
    power_2.value(RELAY_STATE_OFF)
    power_3.value(RELAY_STATE_OFF)
relay_map = {
    b'\x11': power_0,
    b'\x21': power_1,
    b'\x31': power_2,
    b'\x41': power_3,
}
touch_led_states = {
    b'\x11': 0xA0,
    b'\x21': 0xB0,
    b'\x31': 0xC0,
    b'\x41': 0xD0,
}


def handle_touch_input_code(_tic: bytes) -> tuple[bool, str]:
    if _tic not in touch_led_states:
        return False, 'Invalid Touch Input Code'

    # compute new led state
    target_led_state = touch_led_states[_tic]
    new_led_state = target_led_state - 1 if target_led_state % 2 == 1 else target_led_state + 1
    touch_led_states[_tic] = new_led_state

    # control target relay
    new_relay_state = RELAY_STATE_ON if new_led_state % 2 == 1 else RELAY_STATE_OFF
    if sys.implementation.name == 'micropython':
        target_relay = relay_map[_tic]
        target_relay.value(new_relay_state)

    # control target touch led
    if touch_panel_uart:
        touch_panel_uart.write(bytes([new_led_state]))

    return True, 'RELAY_STATE_ON' if new_relay_state == RELAY_STATE_ON else 'RELAY_STATE_OFF'


def detach_uart_0():
    global touch_panel_uart
    _log.ilog('Detaching REPL from UART_0')
    machine.Pin(2, machine.Pin.OUT).value(0)
    touch_panel_uart = os.dupterm(None, 1)


def mod_setup():
    _rpc.add_handler('command_power_0', lambda _: handle_touch_input_code(b'\x11'))
    _rpc.add_handler('command_power_1', lambda _: handle_touch_input_code(b'\x21'))
    _rpc.add_handler('command_power_2', lambda _: handle_touch_input_code(b'\x31'))
    _rpc.add_handler('command_power_3', lambda _: handle_touch_input_code(b'\x41'))
    _rpc.add_handler('state_power_0', lambda _: (True, 'RELAY_STATE_ON') if touch_led_states[b'\x11'] % 2 == 1 else (True, 'RELAY_STATE_OFF'))
    _rpc.add_handler('state_power_1', lambda _: (True, 'RELAY_STATE_ON') if touch_led_states[b'\x21'] % 2 == 1 else (True, 'RELAY_STATE_OFF'))
    _rpc.add_handler('state_power_2', lambda _: (True, 'RELAY_STATE_ON') if touch_led_states[b'\x31'] % 2 == 1 else (True, 'RELAY_STATE_OFF'))
    _rpc.add_handler('state_power_3', lambda _: (True, 'RELAY_STATE_ON') if touch_led_states[b'\x41'] % 2 == 1 else (True, 'RELAY_STATE_OFF'))


async def mod_loop():
    _log.ilog('Running Module Task: ' + MODULE_NAME)
    while True:
        if sys.implementation.name == 'micropython' and touch_panel_uart:
            if touch_panel_uart.any() > 0:
                tic = touch_panel_uart.read(1)
                success, new_relay_state = handle_touch_input_code(tic)
                if success:
                    power_pref_idx = int(hex(tic[0])[2]) - 1
                    _mqtt.mqtt_publish(f"state/{_rpc.mqtt_device_id}/power_{power_pref_idx}", new_relay_state)
            await asyncio.sleep(0.01)  # 100 Hz
            continue
        await asyncio.sleep(1)


# autopep8: off
mqtt_gct = 0
async def mqtt_client_loop(mqtt_client_task):
    global mqtt_gct
    while True:
        mqtt_client_task()
        mqtt_gct += 1
        if mqtt_gct >= 50:
            mqtt_gct = 0
            _mqtt.mqtt_publish(f"telem/{_rpc.mqtt_device_id}/mem_free", str(gc.mem_free()))
            gc.collect()
        await asyncio.sleep(0.1)
# autopep8: on


async def boot_zeos():
    # http_tcp_server_task = _rpc.init_zeos_http_tcp_rpc()
    # if not http_tcp_server_task:
    #     return

    mqtt_client_task = _rpc.init_zeos_mqtt_rpc()
    if not mqtt_client_task:
        return

    _rpc.enable_mqtt_remote_logger()
    _log.ilog('WiFi IP: ' + _wifi.get_wifi_ip())
    mod_setup()
    detach_uart_0()

    # http_tcp_server_task = asyncio.create_task(http_tcp_server_task())
    mqtt_client_task = asyncio.create_task(mqtt_client_loop(mqtt_client_task))
    module_task = asyncio.create_task(mod_loop())
    try:
        await asyncio.gather(
            # http_tcp_server_task,
            mqtt_client_task,
            module_task,
        )
    except Exception as e:
        _log.grace_fail(e)


def boot_repl():
    global touch_panel_uart
    import webrepl  # type: ignore
    webrepl.start(password=_dconf.get_conf('system.device_password'))
    touch_panel_uart = os.dupterm(None, 1)


if __name__ == '__main__':
    boot_mode = _dconf.get_conf('system.boot_mode')
    _log.ilog('Boot Mode ' + boot_mode)
    if boot_mode == 'ZEOS':
        asyncio.run(boot_zeos())
    elif boot_mode == 'REPL' and sys.implementation.name == 'micropython':
        boot_repl()
