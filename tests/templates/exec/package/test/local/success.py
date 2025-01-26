import os
import sys

file_flag = os.path.join(os.environ['TARGET_DIR'], 'invoked-success')
with open(file_flag, 'ab'):
    os.utime(file_flag, None)

# success return code
sys.exit(0)
