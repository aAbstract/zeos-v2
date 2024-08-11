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
    conf_fd.write(json.dumps(_conf, indent=2))
    conf_fd.close()


def set_conf(_key: str, _val: str):
    _conf = _read_conf_file()
    _conf[_key] = _val
    _write_conf_file(_conf)


def get_conf(_key: str):
    global _conf
    conf_level = _conf
    _keys = _key.split('.')
    for k in _keys:
        if k in conf_level:
            conf_level = conf_level[k]
        else:
            return None
    return conf_level
