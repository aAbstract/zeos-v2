# autopep8: off
import os
import gc
import sys
import json
import asyncio
import binascii

if sys.implementation.name == 'micropython':
    import micropython # type: ignore
    import machine # type: ignore
    import bluetooth # type: ignore
sys.path.append(os.getcwd())

import lib.device_config as _dconf
import lib.log as _log
import lib.wifi as _wifi
import lib.mqtt as _mqtt
import lib.rpc as _rpc
# autopep8: on


_wifi.wifi_connect()

MODULE_NAME = 'BLE_BRIDGE'
QHT_BLE_DEVICE_TYPE = 1
_IRQ_SCAN_RESULT = micropython.const(5)
_IRQ_SCAN_DONE = micropython.const(6)

_ble: bluetooth.BLE = bluetooth.BLE()
ble_mac_addr_list: set[bytes] = set()
ble_device_type_map: dict[str, int] = {}
ble_debounce: set[bytes] = set()


def ble_irq(event: int, data: tuple):
    if event == _IRQ_SCAN_RESULT:
        addr = bytes(data[1])
        adv_data = bytes(data[4])
        if addr in ble_mac_addr_list and addr not in ble_debounce:
            ble_debounce.add(addr)
            base64_mac_addr = binascii.b2a_base64(addr).decode()[:-1]
            ble_device_type = ble_device_type_map.get(base64_mac_addr, None)
            if not ble_device_type:
                return

            if ble_device_type == QHT_BLE_DEVICE_TYPE:
                handle_qht_ble_packet(addr, adv_data)

    elif event == _IRQ_SCAN_DONE:
        pass


def mod_setup():
    ble_devices = _dconf.get_conf('ble_bridge.ble_devices')
    if ble_devices:
        for _ble_d in ble_devices:
            _mac_addr: str = _ble_d['mac_address']
            _mac_addr_bin = bytes([int(x, 16) for x in _mac_addr.split(':')])
            ble_mac_addr_list.add(_mac_addr_bin)
            base64_mac_addr = binascii.b2a_base64(_mac_addr_bin).decode()[:-1]
            if _ble_d['device_type'] == 'QHT':
                ble_device_type_map[base64_mac_addr] = QHT_BLE_DEVICE_TYPE
    _ble.irq(ble_irq)


def handle_qht_ble_packet(ble_beacon_mac: bytes, ble_adv_data_packet: bytes):
    ble_device_data = {
        'mac_addr': ':'.join(['%2X' % x for x in ble_beacon_mac]),
        'temp': f"{ble_adv_data_packet[-2]} C",
        'humd': f"{ble_adv_data_packet[-1]}%",
    }
    _mqtt.mqtt_publish(f"telem/{_rpc.mqtt_device_id}/ble_bridge", json.dumps(ble_device_data))


async def mod_loop():
    _log.ilog('Running Module Task: ' + MODULE_NAME)
    while True:
        _ble.active(True)
        _ble.gap_scan(100, 30000, 30000)
        await asyncio.sleep(0.1)
        _ble.active(False)
        await asyncio.sleep(0.1)


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
            ble_debounce.clear()
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
    module_task = asyncio.create_task(mod_loop())
    try:
        await asyncio.gather(
            # http_tcp_server_task,
            mqtt_client_task,
            module_task,
        )
    except Exception as e:
        _log.grace_fail(e)


if __name__ == '__main__':
    asyncio.run(boot_zeos())
