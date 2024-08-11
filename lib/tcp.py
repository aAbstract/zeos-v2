import gc
import json
import asyncio

import lib.log as _log
import lib.device_config as _dconf


def _test(args: dict, sw: asyncio.StreamWriter) -> str | None:
    return 'SERVER_ONLINE'


def _get_logs(args: dict, sw: asyncio.StreamWriter) -> str | None:
    device_password = args.get('device_password', None)
    if device_password != _dconf.get_conf('device_password'):
        sw.write('Invalid Device Password'.encode())
        return
    return '\n'.join(_log.get_logs_tail())


def _lwt(args: dict, sw: asyncio.StreamWriter) -> str | None:
    return 'DEVICE_ONLINE'


def _shell(args: dict, sw: asyncio.StreamWriter) -> str | None:
    device_password = args.get('device_password', None)
    script = args.get('script', None)
    if device_password != _dconf.get_conf('device_password'):
        sw.write('Invalid Device Password'.encode())
        return
    if not script:
        sw.write('Missing `script` Key'.encode())
        return
    try:
        return str(eval(script))
    except Exception as e:
        sw.write(f"Shell Error: {e}".encode())


class TCPServer:
    ''' Warning: using this module will disable python automatic gc '''
    _instance_id: int = 0

    host: str
    port: int
    instance_id: int
    handlers_map: dict

    async def _core_handler(self, sr: asyncio.StreamReader, sw: asyncio.StreamWriter):
        _log.dlog('Received Connection from ' + str(sw.get_extra_info('peername')), 'lib.tcp.TCPServer._core_handler')
        rpc_call = await sr.readline()
        rpc_call = rpc_call[:-1].decode()
        rpc_call_parts = rpc_call.split(' ', 1)
        func_name = rpc_call_parts[0]
        args = {}
        try:
            args = json.loads(rpc_call_parts[1])
        except:
            pass
        if func_name in self.handlers_map:
            res: str | None = self.handlers_map[func_name](args, sw)
            if res:
                sw.write(res.encode())
        else:
            sw.write(f"Invalid RPC Call `{func_name}`".encode())
        sw.close()
        await sw.wait_closed()
        gc.collect()

    def __init__(self) -> None:
        self.instance_id = TCPServer._instance_id
        TCPServer._instance_id += 1
        self.host = '0.0.0.0'
        self.port = int('654' + str(self.instance_id))
        self.handlers_map = {
            'test': _test,
            'get_logs': _get_logs,
            'lwt': _lwt,
            'shell': _shell,
        }

    async def server_task(self):
        log_src = 'lib.tcp.TCPServer.server_task'
        _log.ilog(f"Registered TCPServer_{self.instance_id} Task", log_src)
        await asyncio.start_server(self._core_handler, self.host, self.port)
        _log.ilog(f"TCP Server Running on {self.host}:{self.port}", log_src)

    def add_rpc_handler(self, func_name, func):
        self.handlers_map[func_name] = func
