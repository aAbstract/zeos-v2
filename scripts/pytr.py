# autopep8: off
import os
import sys
import pytest

sys.path.append(os.getcwd())
sys.path.append(os.getcwd() + '/test')
# autopep8: on


if __name__ == '__main__':
    target_tests = [
        os.getcwd() + '/test/test_switch_module_mqtt.py',
    ]
    sys.exit(pytest.main(target_tests))
