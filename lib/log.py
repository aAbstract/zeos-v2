import asyncio
import time


MODULE_ID = 'lib.log'


def _fmt_datetime() -> str:
    current_time = time.localtime(time.time())
    hh = current_time[3]
    mm = current_time[4]
    ss = current_time[5]
    return f"{hh}:{mm}:{ss}"


_log_cache: list[str] = []


async def _save_log_task():
    global _log_cache
    while True:
        if len(_log_cache) == 0:
            return

        log_fd = open('fs/sys.log', 'a')
        log_fd.write('\n'.join(_log_cache) + '\n')
        log_fd.close()
        _log_cache = []

        asyncio.sleep(1)


def _fmt_log(log_type: str, src: str, msg: str) -> str:
    return f"[{_fmt_datetime()}] [{log_type}] - {src}: {msg}"


def ilog(msg: str, src: str = ''):
    log_msg = _fmt_log('INFO', src, msg)
    print(log_msg)
    _log_cache.append(log_msg)


def elog(msg: str, src: str = ''):
    log_msg = _fmt_log('ERROR', src, msg)
    print(log_msg)
    _log_cache.append(log_msg)


def dlog(msg: str, src: str = ''):
    log_msg = _fmt_log('DEBUG', src, msg)
    print(log_msg)
    _log_cache.append(log_msg)


asyncio.run(_save_log_task())
