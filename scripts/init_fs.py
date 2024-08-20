import os
import sys
import json
from uuid import uuid4
from glob import glob
import subprocess

DEV_PORT = '/dev/ttyUSB0'


def load_conf() -> dict:
    conf_fd = open('fs/conf.json', 'r')
    conf = json.loads(conf_fd.read())
    conf_fd.close()
    return conf


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Missing Module Name, Usage: init_fs.py <module_name> [ul: update lib | (sl): skip lib]')
        sys.exit(1)

    target_module = sys.argv[1]
    if len(sys.argv) == 3:
        init_fs_mode = sys.argv[2]
    else:
        init_fs_mode = 'sl'

    print('Building...')
    os.system('rm build/*')
    for py_file in glob('lib/*.py'):
        py_file_name = py_file.split('/')[-1].split('.')[0]
        print(f"Compiling {py_file_name}...")
        os.system(f"bin/mpy-cross {py_file} -o build/{py_file_name}.mpy")
    print('Building...OK')

    print('Removing Current FS...')
    if init_fs_mode == 'ul':
        os.system(f"rshell -p {DEV_PORT} rm -r /pyboard/*")
    elif init_fs_mode == 'sl':
        os.system(f"rshell -p {DEV_PORT} rm -r /pyboard/fs")
    print('Removing Current FS......OK')

    print('Creating New FS...')
    # os.system('find . -type d -name "__pycache__" | xargs rm -r')
    _conf = load_conf()
    device_uuid = str(uuid4())
    with open('fs/conf.json', 'w') as conf_fd:
        _conf['device_uuid'] = device_uuid
        conf_fd.write(json.dumps(_conf))
    if init_fs_mode == 'ul':  # update lib mode
        os.system(f"rshell -p {DEV_PORT} mkdir /pyboard/lib")
        os.system(f"rshell -p {DEV_PORT} cp build/* /pyboard/lib")
    os.system(f"rshell -p {DEV_PORT} mkdir /pyboard/fs && rshell -p {DEV_PORT} cp fs/conf.json /pyboard/fs")
    print('Creating New FS...OK')
    print('Device UUID:', device_uuid)
    with open('fs/conf.json', 'w') as conf_fd:
        _conf['device_uuid'] = '00000000-0000-0000-0000-000000000000'
        conf_fd.write(json.dumps(_conf))
    print(f"Creating New Entry Point: modules/{target_module}.py -> main.py...")
    os.system(f"rshell -p {DEV_PORT} cp modules/{target_module}.py /pyboard/main.py")
    # os.system(f"rshell -p {DEV_PORT} cp fs/webrepl_cfg.py /pyboard/")
    print('Creating New Entry Point...OK')

    # validate
    print('Validating Device FS...')
    cmd_res = subprocess.run(f"rshell -p {DEV_PORT} ls /pyboard/", shell=True, capture_output=True, text=True)
    device_fs = set(cmd_res.stdout.split('\n')[-2].strip().split())
    target_fs = {'lib/', 'fs/', 'main.py'}
    if device_fs != target_fs:
        print(f"Validating Device FS...ERR: device_fs={device_fs}, target_fs={target_fs}")
        sys.exit(1)
    print('Validating Device FS...OK')
