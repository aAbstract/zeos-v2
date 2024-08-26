import gc
import io
import sys
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


def out_log(log_msg: str):
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
    out_log(log_msg)


def elog(msg: str):
    if log_level_bits[1] == '0':
        return
    log_msg = _fmt_log('ERROR', msg)
    out_log(log_msg)


def dlog(msg: str):
    if log_level_bits[2] == '0':
        return
    log_msg = _fmt_log('DEBUG', msg)
    out_log(log_msg)


def grace_fail(_exception: Exception):
    exception_details = io.StringIO()
    if sys.implementation.name == 'micropython':
        sys.print_exception(_exception, exception_details)
    elif sys.implementation.name == 'cpython':
        import traceback
        traceback.print_exception(_exception, file=exception_details)
    exception_details = exception_details.getvalue()
    out_log(exception_details)
    time.sleep(2)

    current_time = time.localtime(time.time())
    year = current_time[0]
    month = current_time[1]
    day = current_time[2]
    hour = current_time[3]
    minute = current_time[4]
    second = current_time[5]
    fmt_time_stamp = f"{year}{month:0>2}{day:0>2}_{hour:0>2}{minute:0>2}{second:0>2}"
    with open(f"fs/sys_fail_{fmt_time_stamp}.log", 'w') as f:
        f.write(exception_details)

    gc.collect()
    gc.enable()
    sys.exit()
