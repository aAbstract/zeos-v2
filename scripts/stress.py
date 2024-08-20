import os
import sys

for i in range(100):
    print('Running Test Iteration', i, '...')
    exit_code = os.system('python scripts/pytr.py')
    if exit_code != 0:
        print('Test Iteration', i, '...ERR')
        sys.exit(exit_code)
