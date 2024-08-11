import json
import subprocess
import lib.device_config as _dconf

# API_URL = 'http://192.168.69.125:8080/api'
# device_uuid = '5c15e368-88b7-46ac-87cf-a699116141b8'

API_URL = 'http://127.0.0.1:8080/api'
device_uuid = '00000000-0000-0000-0000-000000000000'

# TCP_SERVER = '127.0.0.1'
# TCP_PORT = 6540

# TCP_SERVER = '192.168.178.125'
TCP_SERVER = '192.168.69.125'
TCP_PORT = 6540


def make_tcp_request(rpc_call: str, args: dict = {}, add_password: bool = False) -> str:
    if add_password:
        args['device_password'] = _dconf.get_conf('device_password')
    cmd = f"echo '{rpc_call} {json.dumps(args)}' | nc {TCP_SERVER} {TCP_PORT}"
    cmd_res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cmd_res.stdout.decode()
