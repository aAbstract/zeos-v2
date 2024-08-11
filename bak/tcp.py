import asyncio
import socket
import sys

import lib.log as _log


shell_locals: dict = {}


async def handle_client(client: socket.socket):
    request = None
    while request != 'quit':
        request = client.recv(255).decode()
        print('Handling ' + request)
        response = str(eval(request, globals(), shell_locals)) + '\n'
        client.sendall(response.encode())
    client.close()


async def run_server(_shell_locals: dict):
    global shell_locals
    shell_locals = _shell_locals
    log_src = 'lib.tcp.run_server'
    _log.ilog('Registered TCP Server Task', log_src)
    port = 6543
    server = socket.socket()
    server.bind(socket.getaddrinfo('0.0.0.0', port)[0][-1])
    server.setblocking(False)
    loop = asyncio.get_event_loop()
    server.listen(1)
    _log.ilog('TCP Server Listening on Port ' + str(port), log_src)
    while True:
        try:
            client, client_addr = server.accept()
            _log.ilog('Received Connection From ' + str(client_addr), log_src)
            loop.create_task(handle_client(client))
        except OSError:
            pass
