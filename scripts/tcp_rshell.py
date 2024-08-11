import sys
import readline
import subprocess
import json
from rlcompleter import Completer


def shell_loop(host: str, port: int):
    shell_password = 'device_pass_123'
    readline.set_completer(Completer().complete)
    readline.parse_and_bind("tab: complete")
    while True:
        script = input('> ')
        shell_rpc_args = {
            'device_password': shell_password,
            'script': script,
        }
        cmd_res = subprocess.run(f"echo 'shell {json.dumps(shell_rpc_args)}' | nc {host} {port}", shell=True, capture_output=True, text=True).stdout
        if not cmd_res:
            print(f"Error Executing Script: {script}, cmd_res={cmd_res}")
            continue
        print(cmd_res)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python tcp_rshell.py <host> <port>')
        sys.exit(1)

    host = sys.argv[1]
    port = sys.argv[2]

    # test connection
    print(f"Connecting to ZEOS {host}...")
    try:
        cmd_res = subprocess.run(f"echo 'test' | nc {host} {port}", shell=True, capture_output=True, text=True)
        is_connected = cmd_res.stdout == 'SERVER_ONLINE'
        if is_connected:
            print(f"Connecting to ZEOS {host}...OK")
            shell_loop(host, int(port))
    except:
        print('Disconnected')
