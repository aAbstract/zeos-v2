import json
import subprocess
import lib.device_config as _dconf

RPC_SERVER_ADDR = '127.0.0.1'
# RPC_SERVER_ADDR = '192.168.178.125'
# RPC_SERVER_ADDR = '192.168.69.125'
# RPC_SERVER_ADDR = '192.168.178.233'
# RPC_SERVER_ADDR = '192.168.192.104'
# RPC_SERVER_ADDR = '192.168.192.104'
# RPC_SERVER_ADDR = '192.168.192.105'
RPC_SERVER_PORT = 6540
API_URL = f"http://{RPC_SERVER_ADDR}:{RPC_SERVER_PORT}/rpc"


def make_tcp_request(rpc_call: str, args: dict = {}, add_password: bool = False) -> str:
    if add_password:
        args['device_password'] = _dconf.get_conf('system.device_password')
    cmd = f"echo '{rpc_call} {json.dumps(args)}' | nc {RPC_SERVER_ADDR} {RPC_SERVER_PORT}"
    cmd_res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return cmd_res.stdout
