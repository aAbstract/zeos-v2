import time

import lib.device_config as _dconf
import lib.mediator as _mediator


MODULE_ID = 'lib.log'
logs_cache: list[str] = []
log_level_bits = bin(_dconf.get_conf('system.log_level'))[2:]
_enable_remote_logger = False


def _fmt_datetime() -> str:
    current_time = time.localtime(time.time())
    hh = current_time[3]
    mm = current_time[4]
    ss = current_time[5]
    return f"{hh}:{mm}:{ss}"


def _fmt_log(log_type: str, src: str, msg: str) -> str:
    return f"[{_fmt_datetime()}] [{log_type}] - {src}: {msg}"


def _out_log(log_msg: str):
    if not _enable_remote_logger:
        print(log_msg)
        logs_cache.append(log_msg)
    else:
        _mediator.post_event('network_log', log_msg)


def enable_remote_logger():
    global _enable_remote_logger
    _enable_remote_logger = True


def ilog(msg: str, src: str = ''):
    if log_level_bits[0] == '0':
        return
    log_msg = _fmt_log('INFO', src, msg)
    _out_log(log_msg)


def elog(msg: str, src: str = ''):
    if log_level_bits[1] == '0':
        return
    log_msg = _fmt_log('ERROR', src, msg)
    _out_log(log_msg)


def dlog(msg: str, src: str = ''):
    if log_level_bits[2] == '0':
        return
    log_msg = _fmt_log('DEBUG', src, msg)
    _out_log(log_msg)
