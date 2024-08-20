# autopep8: off
import os
import sys
import pytest

sys.path.append(os.getcwd())
sys.path.append(os.getcwd() + '/test')
# autopep8: on


if __name__ == '__main__':
    sys.exit(pytest.main())
