import asyncio
import json
from lib.microdot import Microdot, Request
import lib.device_config as _dconf


server = Microdot()


def _wrap_json_string(inp: str) -> str:
    return '"' + inp + '"'


@server.before_request
async def parse_json_body(request: Request):
    req_body = request.body
    if not req_body:
        return

    try:
        json_body = json.loads(req_body)
        request.g.json_body = json_body
    except:
        return


@server.route(_dconf.get_conf('http.api_root') + '/test', methods=['GET'])
async def test(_: Request):
    return _wrap_json_string('SERVER_ONLINE')


@server.route(_dconf.get_conf('http.api_root') + '/shell', methods=['POST'])
async def shell(request: Request):
    req_headers: dict = request.headers
    device_password = req_headers.get('x-device-password', None)
    if device_password != _dconf.get_conf('device_password'):
        return _wrap_json_string('UNAUTHORIZED'), 401

    json_body = request.g.json_body
    if not json_body:
        return _wrap_json_string('Missing JSON Body'), 400

    if 'script' not in json_body:
        return _wrap_json_string('Missing `script` Key'), 400

    _script = json_body['script']
    return _wrap_json_string(eval(_script))


def start_http_server():
    asyncio.run(server.start_server(host='0.0.0.0', port=8080, debug=True, ssl=None))
