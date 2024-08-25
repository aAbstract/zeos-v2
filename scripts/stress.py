import os
import sys
import time

for i in range(50):
    print('Running Test Iteration', i, '...')
    exit_code = os.system('python scripts/pytr.py')
    if exit_code != 0:
        print('Test Iteration', i, '...ERR')
        sys.exit(exit_code)
    time.sleep(1)
