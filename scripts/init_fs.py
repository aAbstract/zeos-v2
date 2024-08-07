import os
import sys
import json
from uuid import uuid4
import subprocess

DEV_PORT = '/dev/ttyUSB0'


def load_conf() -> dict:
    conf_fd = open('fs/conf.json', 'r')
    conf = json.loads(conf_fd.read())
    conf_fd.close()
    return conf


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Missing Module Name, Usage: init_fs.py <module_name>')
        sys.exit(1)

    target_module = sys.argv[1]
    print('Removing Current FS...')
    os.system(f"rshell -p {DEV_PORT} rm -r /pyboard/*")
    print('Removing Current FS......OK')

    print('Creating New FS...')
    os.system('find . -type d -name "__pycache__" | xargs rm -r')
    conf_fd = open('fs/conf.json', 'w')
    device_uuid = uuid4()
    _conf = load_conf()
    _conf['device_uuid'] = device_uuid
    conf_fd.write(json.dumps(_conf, indent=2))
    conf_fd.close()
    os.system(f"rshell -p {DEV_PORT} cp -r drivers lib fs /pyboard/")
    print('Creating New FS...OK')
    print('Device UUID:', device_uuid)

    print(f"Creating New Entry Point: modules/{target_module}.py -> main.py...")
    os.system(f"rshell -p {DEV_PORT} cp modules/{target_module}.py /pyboard/main.py")
    print('Creating New Entry Point...OK')

    # validate
    print('Validating Device FS...')
    cmd_res = subprocess.run([
        'rshell',
        '-p',
        DEV_PORT,
        'ls',
        '/pyboard/'
    ], capture_output=True, text=True)
    device_fs = set(cmd_res.stdout.split('\n')[-2].strip().split())
    target_fs = {'drivers/', 'lib/', 'fs/', 'main.py'}
    if device_fs != target_fs:
        print(f"Validating Device FS...ERR: device_fs={device_fs}, target_fs={target_fs}")
        sys.exit(1)
    print('Validating Device FS...OK')
