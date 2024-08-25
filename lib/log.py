import time

import lib.device_config as _dconf
import lib.mediator as _mediator


log_level_bits = bin(_dconf.get_conf('system.log_level'))[2:]
_enable_remote_logger = False


def _fmt_datetime() -> str:
    current_time = time.localtime(time.time())
    hh = current_time[3]
    mm = current_time[4]
    ss = current_time[5]
    return f"{hh}:{mm}:{ss}"


def _fmt_log(log_type: str, msg: str) -> str:
    return f"[{_fmt_datetime()}] [{log_type}] {msg}"


def _out_log(log_msg: str):
    if not _enable_remote_logger:
        print(log_msg)
    else:
        _mediator.post_event('network_log', log_msg)


def enable_remote_logger():
    global _enable_remote_logger
    _enable_remote_logger = True


def ilog(msg: str):
    if log_level_bits[0] == '0':
        return
    log_msg = _fmt_log('INFO', msg)
    _out_log(log_msg)


def elog(msg: str):
    if log_level_bits[1] == '0':
        return
    log_msg = _fmt_log('ERROR', msg)
    _out_log(log_msg)


def dlog(msg: str):
    if log_level_bits[2] == '0':
        return
    log_msg = _fmt_log('DEBUG', msg)
    _out_log(log_msg)
