import sys
import json
from paho.mqtt.client import Client as MQTTClient


_conf_path = 'fs/conf.json'
_conf: dict = None
with open(_conf_path, 'r') as f:
    _conf = json.loads(f.read())

device_uuid = sys.argv[1]
mqtt_client = MQTTClient(client_id='mqtt_log_mon', clean_session=True)
mqtt_client.username_pw_set(_conf['mqtt']['username'], _conf['mqtt']['password'])
device_log_topic = 'telem/' + device_uuid + '/log'
print('Connecting to MQTT Logs Channel:', device_log_topic, '...')
mqtt_client.connect(_conf['mqtt']['broker'])


# autopep8: off
def mqtt_on_connect(mqtt_client, _2, _3, rc):
    if rc == 0:
        print('Connecting to MQTT Logs Channel:', device_log_topic, '...OK')
    else:
        print('Connecting to MQTT Logs Channel:', device_log_topic, '...ERR')
mqtt_client.on_connect = mqtt_on_connect
# autopep8: on

mqtt_client.subscribe(device_log_topic)
mqtt_client.on_message = lambda _1, _2, msg: print(msg.payload.decode())

while True:
    mqtt_client.loop(0.1)
