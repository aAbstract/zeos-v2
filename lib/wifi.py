# autopep8: off
import re
import time
import sys
if sys.implementation.name == 'micropython':
    import network # type: ignore
    import machine # type: ignore
elif sys.implementation.name == 'cpython':
    import subprocess

import lib.device_config as _dconf
import lib.log as _log
# autopep8: on


_wifi_ip = None


def _wifi_connect_esp():
    global _wifi_ip
    wifi_ssid = _dconf.get_conf('wifi.ssid')
    wifi_password = _dconf.get_conf('wifi.password')
    _log.dlog(f"ESP Connecting to WiFi ssid={wifi_ssid}, wifi_password={wifi_password}...")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.disconnect()
    sta_if.connect(wifi_ssid, wifi_password)
    while not sta_if.isconnected():
        print('.', end='')
        machine.Pin(2, machine.Pin.OUT).value(0)
        time.sleep(0.5)
        machine.Pin(2, machine.Pin.OUT).value(1)
        time.sleep(0.5)
    _log.ilog('ESP Connecting to WiFi...OK')
    _wifi_ip = sta_if.ifconfig()[0]
    _log.ilog('ESP WiFi IP ' + sta_if.ifconfig()[0])


def _wifi_connect_unix():
    global _wifi_ip
    _log.ilog('Unix Connecting to WiFi...')
    cmd_res = subprocess.run('ifconfig', shell=True, capture_output=True, text=True)
    wifi_ip = re.findall(r'wlo[0-9]:.*\n\s+inet\s(.*)\s{2}netmask', cmd_res.stdout)
    if wifi_ip:
        _log.ilog('Unix Connecting to WiFi...OK')
        _wifi_ip = wifi_ip[0]
        _log.ilog('Unix WiFi IP ' + wifi_ip[0])
    else:
        _log.elog('Unix Connecting to WiFi...ERR')


def get_wifi_ip() -> str | None:
    return _wifi_ip


def wifi_connect():
    if sys.implementation.name == 'micropython':
        _wifi_connect_esp()
    elif sys.implementation.name == 'cpython':
        _wifi_connect_unix()
