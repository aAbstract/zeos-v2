import time


MODULE_ID = 'lib.log'
LOG_FILE_PATH = 'fs/sys.log'


def _fmt_datetime() -> str:
    current_time = time.localtime(time.time())
    hh = current_time[3]
    mm = current_time[4]
    ss = current_time[5]
    return f"{hh}:{mm}:{ss}"


def _save_log(_log: str):
    try:
        log_fd = open(LOG_FILE_PATH, 'a')
    except OSError:
        log_fd = open(LOG_FILE_PATH, 'w')
    log_fd.write(_log + '\n')
    log_fd.close()


def _fmt_log(log_type: str, src: str, msg: str) -> str:
    return f"[{_fmt_datetime()}] [{log_type}] - {src}: {msg}"


def get_logs_tail() -> list[str]:
    logs_fd = open(LOG_FILE_PATH, 'r')
    logs = logs_fd.read()
    logs_fd.close()
    return logs.split('\n')[-5:]


def ilog(msg: str, src: str = ''):
    log_msg = _fmt_log('INFO', src, msg)
    print(log_msg)
    _save_log(log_msg)


def elog(msg: str, src: str = ''):
    log_msg = _fmt_log('ERROR', src, msg)
    print(log_msg)
    _save_log(log_msg)


def dlog(msg: str, src: str = ''):
    log_msg = _fmt_log('DEBUG', src, msg)
    print(log_msg)
