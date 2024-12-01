# autopep8: off
import os
import gc
import sys
import asyncio

if sys.implementation.name == 'micropython':
    import machine # type: ignore
sys.path.append(os.getcwd())

import lib.log as _log
import lib.wifi as _wifi
import lib.mqtt as _mqtt
import lib.rpc as _rpc
# autopep8: on


_wifi.wifi_connect()

MODULE_NAME = 'SWITCH_1CH'
RELAY_STATE_ON = 0
RELAY_STATE_OFF = 1

power_0 = None
power_0_state = RELAY_STATE_OFF
if sys.implementation.name == 'micropython':
    power_0 = machine.Pin(5, machine.Pin.OUT)
    power_0.value(RELAY_STATE_OFF)


def toggle_power_0():
    new_relay_state = RELAY_STATE_ON if power_0_state == RELAY_STATE_OFF else RELAY_STATE_ON
    power_0.value(new_relay_state)
    _mqtt.mqtt_publish(f"state/{_rpc.mqtt_device_id}/power_0", new_relay_state, retain=True)


def mod_setup():
    _rpc.add_handler('command_power_0', lambda _: toggle_power_0())
    _rpc.add_handler('state_power_0', lambda _: (True, 'RELAY_STATE_ON') if power_0 == RELAY_STATE_ON else (True, 'RELAY_STATE_OFF'))


async def mod_loop():
    _log.ilog('Running Module Task: ' + MODULE_NAME)
    while True:
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
            _mem_free = str(gc.mem_free())
            _log.dlog('Free Memory: '+ _mem_free)
            _mqtt.mqtt_publish(f"telem/{_rpc.mqtt_device_id}/mem_free", _mem_free)
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

    # _rpc.enable_mqtt_remote_logger()
    _log.ilog('WiFi IP: ' + _wifi.get_wifi_ip())
    mod_setup()

    # http_tcp_server_task = asyncio.create_task(http_tcp_server_task())
    mqtt_client_task = asyncio.create_task(mqtt_client_loop(mqtt_client_task))
    # module_task = asyncio.create_task(mod_loop())
    try:
        await asyncio.gather(
            # http_tcp_server_task,
            mqtt_client_task,
            # module_task,
        )
    except Exception as e:
        _log.grace_fail(e)


if __name__ == '__main__':
    asyncio.run(boot_zeos())
