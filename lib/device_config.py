import json


MODULE_ID = 'lib.device_config'


def _read_conf_file() -> dict:
    conf_fd = open('fs/conf.json', 'r')
    _conf = json.loads(conf_fd.read())
    conf_fd.close()
    return _conf


_conf = _read_conf_file()


def _write_conf_file(_conf: dict):
    conf_fd = open('fs/conf.json', 'w')
    conf_fd.write(json.dumps(_conf))
    conf_fd.close()


def set_conf(_key: str, _val: str):
    global _conf
    conf_root, conf_key = _key.split('.')
    if conf_root not in _conf:
        return None
    if conf_key not in _conf[conf_root]:
        return None
    _conf[conf_root][conf_key] = _val
    _write_conf_file(_conf)


def get_conf(_key: str):
    global _conf
    conf_root, conf_key = _key.split('.')
    if conf_root not in _conf:
        return None
    if conf_key not in _conf[conf_root]:
        return None
    return _conf[conf_root][conf_key]
