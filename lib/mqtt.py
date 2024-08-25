import sys

import lib.log as _log
import lib.device_config as _dconf


_core_rpc_handler_mqtt = None
_mqtt_client = None


def _paho_mqtt_on_connect(mqtt_client, _2, _3, rc):
    global _mqtt_client
    if rc == 0:
        _mqtt_client = mqtt_client
        _log.ilog('Paho Connecting to MQTT Broker...OK')
    else:
        _log.elog('Paho Connecting to MQTT Broker...ERR')


def _paho_mqtt_on_message(_1, _2, msg):
    if not _core_rpc_handler_mqtt:
        return
    _core_rpc_handler_mqtt(msg.topic, msg.payload.decode())


def _umqtt_on_message(topic: bytes, payload: bytes):
    if not _core_rpc_handler_mqtt:
        return
    _core_rpc_handler_mqtt(topic.decode(), payload.decode())


def mqtt_connect_cpython(
    client_id: str,
    mqtt_broker: str,
    mqtt_port: int,
    mqtt_username: str,
    mqtt_password: str,
    mqtt_subscribe_list: list[str],
):
    ''' CPython Connect to MQTT Broker and Return Client Task Function '''
    from paho.mqtt.client import Client as MQTTClient
    _log.dlog(f'CPYTHON Connecting to MQTT Broker mqtt_broker={mqtt_broker}, mqtt_user={mqtt_username}, mqtt_password={mqtt_password}...')
    mqtt_client = MQTTClient(client_id=client_id, clean_session=True, userdata=None)
    mqtt_client.username_pw_set(mqtt_username, mqtt_password)
    mqtt_client.connect(host=mqtt_broker, port=mqtt_port, keepalive=60)
    for subscribe_topic in mqtt_subscribe_list:
        mqtt_client.subscribe(subscribe_topic)
    mqtt_client.on_connect = _paho_mqtt_on_connect
    mqtt_client.on_message = _paho_mqtt_on_message
    return lambda: mqtt_client.loop(timeout=0.0)


def mqtt_connect_micropython(
    client_id: str,
    mqtt_broker: str,
    mqtt_port: int,
    mqtt_username: str,
    mqtt_password: str,
    mqtt_subscribe_list: list[str],
):
    ''' MicroPython Connect to MQTT Broker and Return Client Task Function '''
    global _mqtt_client
    from lib.umqtt import MQTTClient
    _log.dlog(f'MICROPYTHON Connecting to MQTT Broker mqtt_broker={mqtt_broker}, mqtt_user={mqtt_username}, mqtt_password={mqtt_password}...')
    mqtt_client = MQTTClient(client_id=client_id, server=mqtt_broker, port=mqtt_port, user=mqtt_username, password=mqtt_password)
    try:
        mqtt_client.connect()
        _mqtt_client = mqtt_client
        mqtt_client.set_callback(_umqtt_on_message)
        for subscribe_topic in mqtt_subscribe_list:
            mqtt_client.subscribe(subscribe_topic)
        _log.ilog('MICROPYTHON Connecting to MQTT Broker...OK')
        return mqtt_client.check_msg
    except:
        _log.elog('MICROPYTHON Connecting to MQTT Broker...ERR')


def mqtt_connect(
        mqtt_subscribe_list: list[str],
        core_rpc_handler_mqtt,
):
    global _core_rpc_handler_mqtt
    mqtt_broker = _dconf.get_conf('mqtt.broker')
    device_uuid = _dconf.get_conf('system.device_uuid')
    mqtt_port = _dconf.get_conf('mqtt.port')
    mqtt_username = _dconf.get_conf('mqtt.username')
    mqtt_password = _dconf.get_conf('mqtt.password')
    _core_rpc_handler_mqtt = core_rpc_handler_mqtt
    if sys.implementation.name == 'cpython':
        return mqtt_connect_cpython(
            client_id=device_uuid,
            mqtt_broker=mqtt_broker,
            mqtt_port=mqtt_port,
            mqtt_username=mqtt_username,
            mqtt_password=mqtt_password,
            mqtt_subscribe_list=mqtt_subscribe_list,
        )
    elif sys.implementation.name == 'micropython':
        return mqtt_connect_micropython(
            client_id=device_uuid,
            mqtt_broker=mqtt_broker,
            mqtt_port=mqtt_port,
            mqtt_username=mqtt_username,
            mqtt_password=mqtt_password,
            mqtt_subscribe_list=mqtt_subscribe_list,
        )


def mqtt_publish(topic: str, payload: str):
    if not _mqtt_client:
        return
    if sys.implementation.name == 'cpython':
        _mqtt_client.publish(topic, payload)
    elif sys.implementation.name == 'micropython':
        _mqtt_client.publish(topic.encode(), payload.encode())
