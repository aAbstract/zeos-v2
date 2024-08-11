import sys
import requests
import readline
from rlcompleter import Completer


def shell_loop(base_url: str):
    shell_url = base_url + '/shell'
    shell_password = 'device_pass_123'
    readline.set_completer(Completer().complete)
    readline.parse_and_bind("tab: complete")
    while True:
        cmd = input('> ')
        http_res = requests.post(shell_url, headers={'x-device-password': shell_password}, json={'script': cmd})
        if http_res.status_code != 200:
            print(f"Error Executing cmd: {cmd}, status_code={http_res.status_code}")
            continue
        print(http_res.json())


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python rshell.py <host> <port>')
        sys.exit(1)

    host = sys.argv[1]
    port = sys.argv[2]

    # test connection
    print(f"Connecting to ISI IoT OS {host}...")
    base_url = f"http://{host}:{port}/api"
    try:
        http_res = requests.get(base_url + '/test')
        is_connected = http_res.status_code == 200 and http_res.json() == 'SERVER_ONLINE'
        if is_connected:
            print(f"Connecting to ISI IoT OS {host}...OK")
            shell_loop(base_url)
        else:
            print(f"Connecting to ISI IoT OS {host}...ERR - status_code: {http_res.status_code}")
    except:
        print('Disconnected')
