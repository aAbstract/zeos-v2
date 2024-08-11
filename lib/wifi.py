# autopep8: off
import re
import time
import sys
if sys.implementation.name == 'micropython':
    import network # type: ignore
elif sys.implementation.name == 'cpython':
    import subprocess

import lib.device_config as _dconf
import lib.log as _log
# autopep8: on


def _wifi_connect_esp():
    log_src = 'lib.wifi._wifi_connect_esp'
    wifi_ssid = _dconf.get_conf('wifi.ssid')
    wifi_password = _dconf.get_conf('wifi.password')
    _log.ilog(f"ESP Connecting to WiFi ssid={wifi_ssid}, wifi_password={wifi_password}...", log_src)
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(wifi_ssid, wifi_password)
    while not sta_if.isconnected():
        print('.', end='')
        time.sleep(1)
    _log.ilog('ESP Connecting to WiFi...OK', log_src)
    _log.ilog('ESP WiFi IP ' + sta_if.ifconfig()[0], log_src)


def _wifi_connect_unix():
    log_src = 'lib.wifi.wifi_connect_unix'
    _log.ilog('Unix Connecting to WiFi...', log_src)
    cmd_res = subprocess.run(['ifconfig'], capture_output=True, text=True)
    wifi_ip = re.findall(r'wlo[0-9]:.*\n\s+inet\s(.*)\s{2}netmask', cmd_res.stdout)
    if wifi_ip:
        _log.ilog('Unix Connecting to WiFi...OK', log_src)
        _log.ilog('Unix WiFi IP ' + wifi_ip[0], log_src)
    else:
        _log.elog('Unix Connecting to WiFi...ERR', log_src)


def wifi_connect():
    if sys.implementation.name == 'micropython':
        _wifi_connect_esp()
    elif sys.implementation.name == 'cpython':
        _wifi_connect_unix()
