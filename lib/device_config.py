import json


MODULE_ID = 'lib.device_config'


def _read_conf_file() -> dict:
    conf_fd = open('fs/conf.json', 'r')
    _conf = json.loads(conf_fd.read())
    conf_fd.close()
    return _conf


def _write_conf_file(_conf: dict):
    conf_fd = open('fs/conf.json', 'w')
    conf_fd.write(json.dumps(_conf, indent=2))
    conf_fd.close()


def set_conf(_key: str, _val: str):
    _conf = _read_conf_file()
    _conf[_key] = _val
    _write_conf_file(_conf)


def get_conf(_key: str):
    _keys = _key.split('.')
    _conf = _read_conf_file()
    for k in _keys:
        if k in _conf:
            _conf = _conf[k]
        else:
            return None
    return _conf
