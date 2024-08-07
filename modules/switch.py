# autopep8: off
import os
import sys
import asyncio
sys.path.append(os.getcwd())

import lib.device_config as _dconf
import lib.http as _http
import lib.log as _log
# autopep8: on


MODULE_NAME = 'SWITCH'


def mod_setup():
    log_src = 'modules.switch.mod_setup'
    _log.ilog(f"Setting up Module {MODULE_NAME}...", log_src)
    _http.start_http_server()
    _log.ilog(f"Setting up Module {MODULE_NAME}...OK", log_src)


async def mod_loop():
    while True:
        asyncio.sleep(0.01)  # 100 Hz loop


if __name__ == '__main__':
    mod_setup()
    asyncio.run(mod_loop())
