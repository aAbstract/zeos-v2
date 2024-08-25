import time
from _test_conf import *
from paho.mqtt.client import MQTTMessage
from paho.mqtt.client import Client as MQTTClient


NET_DELAY = 0.1


def test_switch_module_mqtt():
    device_uuid = '0000'
    mqtt_client = MQTTClient(client_id='test.test_switch_module_mqtt', clean_session=True)
    mqtt_client.username_pw_set('isi_muser', 'oE74zxUFEY35JX5ffyx4zUZTSauYS2zCFVhvL6gZe5bsBCQo3tP2pCS5VrH98mvX')
    mqtt_client.connect('127.0.0.1')
    mqtt_client.subscribe(f"state/{device_uuid}/#")
    mqtt_state_map = {}

    def mqtt_msg_handler(_1, _2, msg: MQTTMessage):
        mqtt_state_map[msg.topic] = msg.payload.decode()
    mqtt_client.on_message = mqtt_msg_handler

    for i in range(4):
        mqtt_client.publish(f"rpc/{device_uuid}/command_power_{i}", 'X')
        time.sleep(NET_DELAY)
    while len(mqtt_state_map.keys()) != 4:
        mqtt_client.loop(0.1)
    assert mqtt_state_map == {
        f'state/{device_uuid}/power_0': 'RELAY_STATE_ON',
        f'state/{device_uuid}/power_1': 'RELAY_STATE_ON',
        f'state/{device_uuid}/power_2': 'RELAY_STATE_ON',
        f'state/{device_uuid}/power_3': 'RELAY_STATE_ON',
    }
    mqtt_state_map = {}

    for i in range(4):
        mqtt_client.publish(f"rpc/{device_uuid}/command_power_{i}", 'X')
    while len(mqtt_state_map.keys()) != 4:
        mqtt_client.loop(0.1)
    assert mqtt_state_map == {
        f'state/{device_uuid}/power_0': 'RELAY_STATE_OFF',
        f'state/{device_uuid}/power_1': 'RELAY_STATE_OFF',
        f'state/{device_uuid}/power_2': 'RELAY_STATE_OFF',
        f'state/{device_uuid}/power_3': 'RELAY_STATE_OFF',
    }
