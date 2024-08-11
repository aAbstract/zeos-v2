# autopep8: off
import gc
import sys
import json

if sys.implementation.name == 'micropython':
    import micropython # type: ignore
from bak.microdot import Microdot, Request
import lib.device_config as _dconf
import lib.log as _log
# autopep8: on


class HTTPService:
    _instance_id: int = 0

    port: int
    mdt_server: Microdot
    instance_id: int

    @staticmethod
    def wrap_json_string(inp: str) -> str:
        return '"' + inp + '"'

    def __init__(self):
        self.mdt_server = Microdot()
        self.instance_id = HTTPService._instance_id
        HTTPService._instance_id += 1
        self.port = int('808' + str(self.instance_id))

        @self.mdt_server.before_request
        async def parse_json_body(request: Request):
            print(micropython.mem_info())
            gc.collect()
            req_body = request.body
            if not req_body:
                request.g.json_body = None
                return
            try:
                json_body = json.loads(req_body)
                request.g.json_body = json_body
            except:
                return

        @self.mdt_server.route(_dconf.get_conf('http.api_root') + '/test', methods=['GET'])
        async def test(_: Request):
            return HTTPService.wrap_json_string('SERVER_ONLINE')

        @self.mdt_server.route(_dconf.get_conf('http.api_root') + '/logs', methods=['GET'])
        async def logs(request: Request):
            req_headers: dict = request.headers
            device_password = req_headers.get('x-device-password', None)
            if device_password != _dconf.get_conf('device_password'):
                return HTTPService.wrap_json_string('UNAUTHORIZED'), 401
            return _log.get_logs()

        @self.mdt_server.route(_dconf.get_conf('http.api_root') + '/telem/' + _dconf.get_conf('device_uuid') + '/DEVICE_LWT', methods=['GET'])
        def handle_lwt_request(_: Request):
            return HTTPService.wrap_json_string('DEVICE_ONLINE')

        @self.mdt_server.route(_dconf.get_conf('http.api_root') + '/shell', methods=['POST'])
        async def shell(request: Request):
            req_headers: dict = request.headers
            device_password = req_headers.get('x-device-password', None)
            if device_password != _dconf.get_conf('device_password'):
                return HTTPService.wrap_json_string('UNAUTHORIZED'), 401

            json_body = request.g.json_body
            if not json_body:
                return HTTPService.wrap_json_string('Missing JSON Body'), 400

            if 'script' not in json_body:
                return HTTPService.wrap_json_string('Missing `script` Key'), 400

            _script = json_body['script']
            return HTTPService.wrap_json_string(str(eval(_script)))

    async def server_task(self):
        _log.ilog('Registered HTTP Server Task', 'HTTPServer_' + str(self.instance_id))
        await self.mdt_server.start_server(host='0.0.0.0', port=self.port, debug=True, ssl=None)
